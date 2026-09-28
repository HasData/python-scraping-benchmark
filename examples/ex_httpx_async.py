import asyncio

import httpx

async def main():
    async with httpx.AsyncClient(timeout=20) as client:
        pages = await asyncio.gather(
            *[client.get("https://www.scrapethissite.com/pages/simple/",
                         params={"page_num": n}) for n in (1, 2, 3)]
        )
    print([r.status_code for r in pages])

asyncio.run(main())
