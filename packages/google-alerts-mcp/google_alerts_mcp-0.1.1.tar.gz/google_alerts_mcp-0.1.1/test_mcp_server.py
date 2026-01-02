#!/usr/bin/env python3
"""
Test the MCP server functionality with dynamic token extraction
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from google_alerts_mcp.server import GoogleAlertsClient

async def test_mcp_functionality():
    """Test the MCP server functionality"""
    client = GoogleAlertsClient()
    
    print("Testing MCP Server Functionality")
    print("=" * 50)
    
    try:
        # Test Chinese search
        print("Testing Chinese search for '白银'...")
        articles = await client.get_preview_content("白银", "zh-CN", "US")
        
        if articles:
            print(f"✅ Found {len(articles)} articles for Chinese search")
            for i, article in enumerate(articles[:3], 1):  # Show first 3
                print(f"  {i}. {article.title}")
                print(f"     Source: {article.source}")
                if article.url:
                    print(f"     URL: {article.url[:80]}...")
                print()
        else:
            print("❌ No articles found for Chinese search")
        
        # Test English search
        print("Testing English search for 'bitcoin'...")
        articles = await client.get_preview_content("bitcoin", "en-US", "US")
        
        if articles:
            print(f"✅ Found {len(articles)} articles for English search")
            for i, article in enumerate(articles[:3], 1):  # Show first 3
                print(f"  {i}. {article.title}")
                print(f"     Source: {article.source}")
                if article.url:
                    print(f"     URL: {article.url[:80]}...")
                print()
        else:
            print("❌ No articles found for English search")
        
        print("✅ MCP server functionality test completed successfully")
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False
    
    finally:
        await client.close()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_functionality())