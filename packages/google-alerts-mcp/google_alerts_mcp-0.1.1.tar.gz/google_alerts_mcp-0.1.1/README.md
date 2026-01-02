# Google Alerts MCP Server

一个基于 MCP (Model Context Protocol) 的 Google Alerts 插件，通过模拟浏览器工作流程来获取特定主题的新闻资讯。该插件能够动态提取 Google Alerts 页面的状态参数，避免被检测和封锁。

本 MCP Server 运行需要科学上网环境，或部署为远端服务。

## 功能特性

- **动态状态提取**：自动从 Google Alerts 页面提取 `window.STATE` 参数
- **防检测机制**：每次请求使用新鲜的令牌和会话 cookies 避免被封锁
- **多语言支持**：支持中文、英文等多种语言搜索
- **浏览器工作流程模拟**：完全模拟浏览器访问流程：访问主页 → 提取 cookies/状态 → 构建预览 URL
- **无硬编码参数**：所有认证令牌和状态参数都动态提取，不使用硬编码值
- **URL清理功能**：可配置是否移除Google重定向参数，直接获取目标新闻链接

## 工作流程

1. **获取初始 cookies**：访问 `https://www.google.com/alerts?hl={language}` 获取初始 cookies
2. **状态参数提取**：从页面中提取 `window.STATE` 参数，包括认证令牌
3. **构建预览 URL**：使用提取的参数和搜索查询构建预览 URL
4. **获取内容**：使用正确的 cookies 和状态参数获取预览页面
5. **文章解析**：从 HTML 响应中提取文章标题、URL、摘要和来源

## 安装

使用 UV 包管理器：

```bash
# 克隆项目
git clone https://github.com/ycrao/google-alerts-mcp.git
cd google-alerts-mcp

# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Windows: .venv\Scripts\activate
# 或者直接
uv run python src/google_alerts_mcp/server.py
```

## 使用方法

### 作为 MCP 服务器运行

在 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "google-alerts": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/google-alerts-mcp/src/google_alerts_mcp/",
        "run",
        "server.py"
      ],
      "env": {}
    }
  }
}
```

或者如果已经发布为包：

```json
{
  "mcpServers": {
    "google-alerts": {
      "command": "uvx",
      "args": ["google-alerts-mcp"],
      "env": {}
    }
  }
}
```

### 可用工具

#### `search_google_alerts`

根据特定主题搜索 Google Alerts 新闻文章。

**参数：**
- `query` (必需): 搜索查询/主题（如 "白银", "bitcoin", "人工智能"）
- `language` (可选): 语言代码（默认: "zh-CN"）
- `region` (可选): 地区代码（默认: "US"）
- `clean_urls` (可选): 是否清理Google重定向参数获取直接链接（默认: true）

**示例：**
```json
{
  "query": "bitcoin",
  "language": "en-US",
  "region": "US",
  "clean_urls": true
}
```

**URL清理功能：**
- 当 `clean_urls=true` 时，会自动移除Google重定向参数，直接返回目标新闻网站的链接
- 当 `clean_urls=false` 时，保留原始的Google重定向URL
- 清理前：`https://www.google.com/url?q=https://example.com/article&sa=U&ved=...`
- 清理后：`https://example.com/article`

## 技术细节

### 动态参数提取

服务器从 `window.STATE` 中提取以下参数：
- `domain`: Google 域名（通常是 "com"）
- `language`: 状态中的语言代码
- `region`: 状态中的地区代码
- `number_param`: 数字参数（因语言而异）
- `locale_format`: 区域格式字符串
- `token`: 认证令牌（避免检测的关键）

### 防检测功能

- 每次请求提取新鲜令牌
- 会话 cookie 持久化
- 正确的浏览器头部
- 无硬编码认证参数
- 令牌提取失败时优雅降级

## 测试

运行测试套件验证功能：

```bash
# 测试完整 MCP 服务器功能
python test_mcp_server.py
```

## 测试示例

```python
# 测试搜索功能
import asyncio
from google_alerts_mcp.server import GoogleAlertsClient

async def test():
    client = GoogleAlertsClient()
    try:
        # 中文搜索
        articles = await client.get_preview_content("白银", "zh-CN")
        for article in articles:
            print(f"标题: {article.title}")
            print(f"链接: {article.url}")
            print(f"摘要: {article.snippet}")
            print(f"来源: {article.source}")
            print("-" * 50)
        
        # 英文搜索（启用URL清理）
        client_clean = GoogleAlertsClient(clean_urls=True)
        articles = await client_clean.get_preview_content("bitcoin", "en-US")
        for article in articles:
            print(f"Title: {article.title}")
            print(f"URL: {article.url}")  # 直接链接，无Google重定向参数
            print(f"Snippet: {article.snippet}")
            print(f"Source: {article.source}")
            print("-" * 50)
        await client_clean.close()
        
        # 英文搜索（保留原始URL）
        client_original = GoogleAlertsClient(clean_urls=False)
        articles = await client_original.get_preview_content("bitcoin", "en-US")
        for article in articles:
            print(f"Title: {article.title}")
            print(f"URL: {article.url}")  # 包含Google重定向参数
            print(f"Snippet: {article.snippet}")
            print(f"Source: {article.source}")
            print("-" * 50)
        await client_original.close()
    finally:
        await client.close()

asyncio.run(test())
```

## 注意事项

1. **动态令牌**：系统现在完全依赖动态提取的令牌，不再使用任何硬编码值
2. **URL清理**：默认启用URL清理功能，可通过 `clean_urls=false` 参数保留原始Google重定向URL
3. **请求频率**：避免过于频繁的请求，建议适当间隔
4. **错误处理**：如果令牌提取失败，请求会优雅失败而不是使用过时的硬编码值
5. **实时状态**：每次搜索都会获取新的状态参数，确保最佳的反检测效果

## 依赖库

- **mcp**: Model Context Protocol 支持
- **httpx**: 异步 HTTP 客户端
- **beautifulsoup4**: HTML 解析
- **pydantic**: 数据验证和序列化

## 许可证

MIT License