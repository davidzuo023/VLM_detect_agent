"""
src/tools/search.py
工具：网络搜索
使用 Tavily 搜索 API 获取最新网络信息。
没有 Tavily Key 时自动降级为提示信息。
"""

import os
from dotenv import load_dotenv

load_dotenv()


def web_search(query: str) -> str:
    """
    调用 Tavily 搜索引擎，返回搜索结果摘要。

    Args:
        query: 搜索关键词

    Returns:
        搜索结果文本
    """
    api_key = os.getenv("TAVILY_API_KEY", "")

    if not api_key or api_key == "tvly-your-key-here":
        return (
            f"【搜索工具未配置】\n"
            f"查询内容：{query}\n"
            f"请在 .env 中配置 TAVILY_API_KEY 以启用网络搜索功能。\n"
            f"免费获取：https://tavily.com"
        )

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query, max_results=5)

        snippets = []
        for i, r in enumerate(results.get("results", []), 1):
            title = r.get("title", "无标题")
            content = r.get("content", "")[:300]
            url = r.get("url", "")
            snippets.append(f"{i}. **{title}**\n{content}\n来源：{url}")

        return "\n\n".join(snippets) if snippets else "未找到相关搜索结果"

    except ImportError:
        return "请安装 tavily-python：pip install tavily-python"
    except Exception as e:
        return f"搜索失败：{str(e)}"
