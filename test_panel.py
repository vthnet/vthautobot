import asyncio

from panel import services

async def main():
    data = await services()

    print(data[:5])

asyncio.run(main())