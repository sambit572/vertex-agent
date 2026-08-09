import asyncio
from tools import _crawl

async def main():
    result = await _crawl("https://html.duckduckgo.com/html/?q=latest+news+AI+agents")
    print("LENGTH:", len(result))
    print(result[:1000])

asyncio.run(main())