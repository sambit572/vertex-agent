import os
import asyncio
import subprocess
from crawl4ai import AsyncWebCrawler

# ---- Tool implementations ----

def open_app(app_name: str) -> str:
    """Open a desktop application by name (Windows)."""
    try:
        os.startfile(app_name)
        return f"Opened {app_name}."
    except FileNotFoundError:
        try:
            subprocess.Popen(app_name, shell=True)
            return f"Attempted to open {app_name} via shell."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"


async def _crawl(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown[:4000]  # cap for context window


def web_search(query: str) -> str:
    """Search DuckDuckGo and return clean Markdown content of the results page."""
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    return asyncio.run(_crawl(url))


def open_browser(url: str) -> str:
    """Fetch a URL and return its content as clean Markdown."""
    if not url.startswith("http"):
        url = "https://" + url
    return asyncio.run(_crawl(url))


# ---- Tool schemas (OpenAI-compatible function calling format) ----

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a desktop application on the user's Windows laptop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the app, e.g. 'chrome', 'notepad', 'code'"}
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for a query and return the results as clean text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Fetch and read the content of a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to open and read"}
                },
                "required": ["url"],
            },
        },
    },
]

# Maps tool name -> actual Python function
TOOL_REGISTRY = {
    "open_app": open_app,
    "web_search": web_search,
    "open_browser": open_browser,
}