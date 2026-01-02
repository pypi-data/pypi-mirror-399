#!/usr/bin/env python3
"""
Google Alerts MCP Server

A Model Context Protocol server that fetches Google Alerts preview content
by simulating the browser workflow described in the requirements.
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote, unquote

import httpx
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertArticle(BaseModel):
    """Google Alert article result"""
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[str] = None


class GoogleAlertsClient:
    """Client for Google Alerts that follows the browser workflow"""
    
    def __init__(self, clean_urls: bool = True):
        """
        Initialize the Google Alerts client
        
        Args:
            clean_urls: If True, removes Google redirect parameters to get direct URLs
        """
        self.clean_urls = clean_urls
        self.session = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            timeout=30.0,
            follow_redirects=True
        )
        self.cookies = {}
        self.state_params = None
    
    def clean_google_redirect_url(self, url: str) -> str:
        """
        Clean Google redirect URLs to get direct target URLs
        
        Args:
            url: The original URL (may contain Google redirect parameters)
            
        Returns:
            The cleaned direct URL or original URL if not a redirect
        """
        if not self.clean_urls:
            return url
            
        try:
            # Handle Google redirect URLs like /url?q=...&sa=...
            if url.startswith('/url?'):
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                
                # Try different parameter names that Google uses
                for param_name in ['url', 'q']:
                    if param_name in query_params and query_params[param_name]:
                        direct_url = query_params[param_name][0]
                        if direct_url.startswith('http'):
                            logger.debug(f"Cleaned redirect URL: {url} -> {direct_url}")
                            return direct_url
                
            # Handle full Google redirect URLs
            elif 'google.com/url?' in url:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                
                for param_name in ['url', 'q']:
                    if param_name in query_params and query_params[param_name]:
                        direct_url = query_params[param_name][0]
                        if direct_url.startswith('http'):
                            logger.debug(f"Cleaned redirect URL: {url} -> {direct_url}")
                            return direct_url
            
            # Handle relative URLs
            elif url.startswith('/'):
                return f"https://www.google.com{url}"
                
        except Exception as e:
            logger.debug(f"Error cleaning URL {url}: {e}")
        
        return url
        
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()
    
    async def get_initial_cookies(self, language: str = "zh-CN") -> bool:
        """
        Step 1: Visit the Google Alerts main page to get initial cookies and extract state parameters
        This simulates opening https://www.google.com/alerts?hl=zh-CN
        """
        try:
            url = f"https://www.google.com/alerts?hl={language}"
            logger.info(f"Getting initial cookies and state from: {url}")
            
            response = await self.session.get(url)
            response.raise_for_status()
            
            # Store cookies for later use
            self.cookies.update(response.cookies)
            
            # Extract window.STATE parameters from the page
            state_params = self.extract_state_parameters(response.text, language)
            if state_params and state_params.get('token'):
                self.state_params = state_params
                logger.info("Successfully extracted state parameters with valid token")
                return True
            else:
                logger.error("Failed to extract valid state parameters with token from live page")
                self.state_params = None
                return False
            
        except Exception as e:
            logger.error(f"Failed to get initial cookies: {e}")
            return False
    
    def extract_state_parameters(self, html_content: str, language: str) -> Optional[dict]:
        """Extract window.STATE parameters from the HTML content"""
        try:
            import re
            
            # Search for window.STATE in the HTML
            state_pattern = r'window\.STATE\s*=\s*(\[.*?\]);'
            match = re.search(state_pattern, html_content, re.DOTALL)
            
            if match:
                state_json = match.group(1)
                logger.debug(f"Found window.STATE: {state_json}")
                
                # Parse the JSON
                state_data = json.loads(state_json)
                
                # Extract relevant parameters from the actual structure
                # Based on s1.txt: window.STATE=[null,[null,null,[null,"com",["en","US"]],null,3,[[1,"",[null,8],2,"en-US",null,null,null,null,null,"0",null,null,"AB2Xq4hcilCERh73EFWJVHXx-io2lhh1EhC8UD8"]]]]
                if len(state_data) >= 2 and state_data[1] and len(state_data[1]) >= 6:
                    main_params = state_data[1]
                    
                    # Extract domain and region info from position 2
                    domain_info = main_params[2] if len(main_params) > 2 else None
                    # Extract user parameters from position 5
                    user_params = main_params[5] if len(main_params) > 5 else None
                    
                    extracted_params = {
                        'domain': 'com',
                        'language': language.split('-')[0],
                        'region': 'US',
                        'number_param': 8,
                        'locale_format': language,
                        'token': None
                    }
                    
                    # Extract domain info if available: [null,"com",["en","US"]]
                    if domain_info and len(domain_info) >= 3:
                        if domain_info[1]:
                            extracted_params['domain'] = domain_info[1]
                        if domain_info[2] and len(domain_info[2]) >= 2:
                            extracted_params['language'] = domain_info[2][0]
                            extracted_params['region'] = domain_info[2][1]
                    
                    # Extract user parameters: [[1,"",[null,8],2,"en-US",null,null,null,null,null,"0",null,null,"AB2Xq4hcilCERh73EFWJVHXx-io2lhh1EhC8UD8"]]
                    if user_params and len(user_params) >= 1 and user_params[0]:
                        user_data = user_params[0]
                        if len(user_data) >= 14:  # Ensure we have enough elements (token is at index 13)
                            # Extract number parameter from position 2: [null,8]
                            if user_data[2] and len(user_data[2]) >= 2:
                                extracted_params['number_param'] = user_data[2][1]
                            
                            # Extract locale format from position 4: "en-US"
                            if user_data[4]:
                                extracted_params['locale_format'] = user_data[4]
                            
                            # Extract token from position 13: "AB2Xq4hcilCERh73EFWJVHXx-io2lhh1EhC8UD8"
                            if len(user_data) > 13 and user_data[13]:
                                extracted_params['token'] = user_data[13]
                    
                    # Validate that we extracted a token
                    if not extracted_params.get('token'):
                        logger.error("Failed to extract token from window.STATE")
                        return None
                    
                    logger.info(f"Successfully extracted parameters: {extracted_params}")
                    return extracted_params
                else:
                    logger.error("window.STATE structure is not as expected")
                    return None
                
        except Exception as e:
            logger.error(f"Error extracting state parameters: {e}")
        
        return None
    
    def get_default_state_params(self, language: str) -> dict:
        """Get default state parameters as fallback - but token must always be extracted dynamically"""
        base_lang = language.split('-')[0]
        
        return {
            'domain': 'com',
            'language': base_lang,
            'region': 'US',
            'number_param': 7 if base_lang == 'zh' else 8,
            'locale_format': f"{base_lang}-Hans-US" if base_lang == 'zh' else language,
            'token': None  # Token must ALWAYS be extracted dynamically, never hardcoded
        }
    
    def build_preview_url(self, query: str, language: str = "zh-CN", region: str = "US") -> str:
        """
        Build the preview URL using dynamically extracted state parameters.
        This follows the structure from the curl example and window.STATE.
        """
        # Use extracted state parameters if available, otherwise use defaults
        if self.state_params:
            params_info = self.state_params
        else:
            params_info = self.get_default_state_params(language)
        
        # Check if we have a valid token - NEVER use hardcoded fallback
        if not params_info.get('token'):
            raise Exception("No valid token available - state parameters must be extracted from live page")
        
        token = params_info['token']
        
        # Build the parameters array using extracted values
        params = [
            None,
            [
                None,
                None,
                None,
                [
                    None,
                    query,  # The search query
                    params_info['domain'],  # Domain from state
                    [None, params_info['language'], params_info['region']],  # Language and region from state
                    None,
                    None,
                    None,
                    0,
                    1
                ],
                None,
                3,
                [
                    [
                        None,
                        1,
                        "user@example.com",  # Placeholder email
                        [None, None, params_info['number_param']],  # Number parameter from state
                        2,
                        params_info['locale_format'],  # Locale format from state
                        None,
                        None,
                        None,
                        None,
                        None,
                        "0",
                        None,
                        None,
                        token  # Dynamic token from state
                    ]
                ]
            ],
            0
        ]
        
        # Convert to JSON and URL encode
        params_json = json.dumps(params, separators=(',', ':'), ensure_ascii=False)
        params_encoded = quote(params_json)
        
        return f"https://www.google.com/alerts/preview?params={params_encoded}&hl={language}"
    
    async def get_preview_content(self, query: str, language: str = "zh-CN", region: str = "US") -> List[AlertArticle]:
        """
        Step 2: Get the preview content by making a request to the preview URL
        Always get fresh cookies and state parameters to avoid being blocked
        """
        try:
            # Always get fresh initial cookies and state parameters for each request
            if not await self.get_initial_cookies(language):
                raise Exception("Failed to get initial cookies and state parameters")
            
            # Verify we have a valid token
            if not self.state_params or not self.state_params.get('token'):
                raise Exception("Failed to extract valid state parameters with token")
            
            # Build the preview URL with fresh state parameters
            preview_url = self.build_preview_url(query, language, region)
            logger.info(f"Fetching preview content for query: {query}")
            logger.debug(f"Preview URL: {preview_url}")
            logger.debug(f"Using token: {self.state_params.get('token')}")
            
            # Make the request with cookies and fresh state
            response = await self.session.get(
                preview_url,
                cookies=self.cookies
            )
            response.raise_for_status()
            
            # Parse the response
            articles = self.parse_preview_response(response.text)
            logger.info(f"Found {len(articles)} articles")
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to get preview content: {e}")
            raise
    
    def parse_preview_response(self, html_content: str) -> List[AlertArticle]:
        """
        Parse the HTML response from Google Alerts preview page
        """
        articles = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Google Alerts uses specific structure: li.result contains each article
            result_items = soup.find_all('li', class_='result')
            logger.debug(f"Found {len(result_items)} result items")
            
            for item in result_items:
                try:
                    article = self.extract_google_alerts_article(item)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing result item: {e}")
                    continue
            
            # If no results found with the specific structure, try fallback methods
            if not articles:
                logger.debug("No articles found with Google Alerts structure, trying fallback methods")
                articles = self.extract_fallback_articles(soup)
            
        except Exception as e:
            logger.error(f"Error parsing preview response: {e}")
        
        return articles
    
    def extract_google_alerts_article(self, item) -> Optional[AlertArticle]:
        """Extract article information from Google Alerts result item"""
        try:
            # Find the title link
            title_link = item.find('a', class_='result_title_link')
            if not title_link:
                return None
            
            # Extract title (remove HTML tags like <b>)
            title = title_link.get_text(strip=True)
            if not title or len(title) < 5:
                return None
            
            # Extract URL
            url = title_link.get('href', '')
            
            # Clean up Google redirect URLs using the configurable method
            url = self.clean_google_redirect_url(url)
            
            # Extract snippet
            snippet = ""
            snippet_elem = item.find('span', class_='snippet')
            if snippet_elem:
                snippet = snippet_elem.get_text(strip=True)
            
            # Extract source
            source = "Google Alerts"
            source_elem = item.find('div', class_='result_source')
            if source_elem:
                source = source_elem.get_text(strip=True)
            
            # Extract domain from URL as fallback source
            if source == "Google Alerts" and url:
                try:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    if parsed_url.netloc:
                        domain = parsed_url.netloc
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        source = domain
                except:
                    pass
            
            return AlertArticle(
                title=title,
                url=url,
                snippet=snippet,
                source=source
            )
            
        except Exception as e:
            logger.debug(f"Error extracting Google Alerts article: {e}")
            return None
    
    def extract_fallback_articles(self, soup) -> List[AlertArticle]:
        """Fallback method to extract articles using generic selectors"""
        articles = []
        
        try:
            # Try multiple selectors as fallback
            selectors = [
                'div[role="article"]',
                '.alert-item',
                '.news-item',
                'article',
                'div[data-ved]',
                '.g'
            ]
            
            found_articles = []
            for selector in selectors:
                found_articles = soup.select(selector)
                if found_articles:
                    logger.debug(f"Fallback: found articles using selector: {selector}")
                    break
            
            # If still no structured articles found, look for links in the page
            if not found_articles:
                all_divs = soup.find_all('div')
                found_articles = [div for div in all_divs if div.find('a', href=True)]
                logger.debug(f"Fallback: found {len(found_articles)} divs with links")
            
            for article_elem in found_articles[:10]:  # Limit to 10 articles
                try:
                    article = self.extract_article_info(article_elem)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing fallback article element: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in fallback article extraction: {e}")
        
        return articles
    
    def extract_article_info(self, element) -> Optional[AlertArticle]:
        """Extract article information from a DOM element"""
        try:
            # Find title and URL
            title_elem = element.find('a', href=True) or element.find('h3') or element.find('h2')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title or len(title) < 5:
                return None
            
            # Get URL
            url = ""
            if title_elem.name == 'a':
                url = title_elem.get('href', '')
            else:
                # Look for a link in the same container
                link_elem = element.find('a', href=True)
                if link_elem:
                    url = link_elem.get('href', '')
            
            # Clean up Google redirect URLs using the configurable method
            url = self.clean_google_redirect_url(url)
            
            # Find snippet/description
            snippet = ""
            snippet_selectors = [
                '.snippet', '.desc', '.description', 'p',
                '[class*="snippet"]', '[class*="desc"]'
            ]
            
            for sel in snippet_selectors:
                snippet_elem = element.select_one(sel)
                if snippet_elem:
                    snippet_text = snippet_elem.get_text(strip=True)
                    if snippet_text and snippet_text != title and len(snippet_text) > 10:
                        snippet = snippet_text
                        break
            
            # If no snippet found, try to get text from the element
            if not snippet:
                all_text = element.get_text(strip=True)
                if title in all_text:
                    remaining_text = all_text.replace(title, '', 1).strip()
                    if len(remaining_text) > 20:
                        snippet = remaining_text[:300] + "..." if len(remaining_text) > 300 else remaining_text
            
            # Find source
            source = "Google Alerts"
            source_selectors = ['cite', '.source', '[class*="source"]', '.site']
            
            for sel in source_selectors:
                source_elem = element.select_one(sel)
                if source_elem:
                    source_text = source_elem.get_text(strip=True)
                    if source_text and len(source_text) < 100:
                        source = source_text
                        break
            
            # Extract domain from URL as fallback source
            if source == "Google Alerts" and url:
                try:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    if parsed_url.netloc:
                        domain = parsed_url.netloc
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        source = domain
                except:
                    pass
            
            # Find published date
            published_date = None
            date_selectors = ['time', '.date', '[class*="date"]', '.published']
            
            for sel in date_selectors:
                date_elem = element.select_one(sel)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    if date_text:
                        published_date = date_text
                        break
            
            if title:
                return AlertArticle(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source=source,
                    published_date=published_date
                )
            
        except Exception as e:
            logger.debug(f"Error extracting article info: {e}")
        
        return None
    
    def extract_from_scripts(self, soup) -> List[AlertArticle]:
        """Try to extract article data from JavaScript/JSON in script tags"""
        articles = []
        
        try:
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Look for JSON-like data that might contain article information
                    script_content = script.string
                    
                    # Try to find URLs and titles in the script content
                    url_pattern = r'https?://[^\s"\'<>]+'
                    urls = re.findall(url_pattern, script_content)
                    
                    for url in urls[:5]:  # Limit to first 5 URLs
                        if any(domain in url for domain in ['news', 'article', 'blog', 'post']):
                            # Create a basic article entry
                            articles.append(AlertArticle(
                                title=f"Article from {url.split('/')[2] if '/' in url else 'Unknown'}",
                                url=url,
                                snippet="Article found in page data",
                                source=url.split('/')[2] if '/' in url else 'Unknown'
                            ))
        
        except Exception as e:
            logger.debug(f"Error extracting from scripts: {e}")
        
        return articles


# Initialize the MCP server
app = Server("google-alerts-mcp")
client = GoogleAlertsClient(clean_urls=True)  # Default to cleaning URLs


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_google_alerts",
            description="Search Google Alerts for news articles about a specific topic by simulating the browser workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query/topic to look for (e.g., '白银', 'artificial intelligence')"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (e.g., 'zh-CN', 'en-US')",
                        "default": "zh-CN"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region code (e.g., 'US', 'CN')",
                        "default": "US"
                    },
                    "clean_urls": {
                        "type": "boolean",
                        "description": "If true, removes Google redirect parameters to get direct target URLs (default: true)",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "search_google_alerts":
        query = arguments.get("query")
        language = arguments.get("language", "zh-CN")
        region = arguments.get("region", "US")
        clean_urls = arguments.get("clean_urls", True)
        
        if not query:
            return [TextContent(type="text", text="Error: query parameter is required")]
        
        # Create a client instance with the specified clean_urls setting
        search_client = GoogleAlertsClient(clean_urls=clean_urls)
        
        try:
            # Get articles from Google Alerts
            articles = await search_client.get_preview_content(query, language, region)
            
            if not articles:
                return [TextContent(
                    type="text",
                    text=f"No articles found for query: {query}"
                )]
            
            # Format the results
            output = f"Google Alerts Results for '{query}':\n\n"
            if clean_urls:
                output += "(URLs cleaned to remove Google redirect parameters)\n\n"
            
            for i, article in enumerate(articles, 1):
                output += f"{i}. **{article.title}**\n"
                if article.url:
                    output += f"   URL: {article.url}\n"
                if article.snippet:
                    output += f"   Summary: {article.snippet}\n"
                output += f"   Source: {article.source}\n"
                if article.published_date:
                    output += f"   Date: {article.published_date}\n"
                output += "\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            error_msg = f"Error searching Google Alerts: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
        finally:
            # Close the temporary client
            await search_client.close()
            await search_client.close()
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main entry point"""
    from mcp.types import ServerCapabilities
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="google-alerts-mcp",
                server_version="0.1.1",
                capabilities=ServerCapabilities(
                    tools={}
                ),
            ),
        )


def cli_main():
    """CLI entry point for package installation"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()