import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import (
    client,
    get_settings,
)
from handlers import routers
from panel import services
from worker import worker

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


async def startup():

    # MongoDB
    await client.admin.command("ping")
    print("✅ MongoDB Connected")

    # Load/Create Settings
    settings = await get_settings()
    print("✅ Settings Loaded")

    # Telegram
    me = await bot.get_me()
    print(f"✅ @{me.username} started successfully")

    # CheapestSMM API
    try:

        data = await services()

        print("✅ CheapestSMM Connected")
        print(f"📦 Total Services: {len(data)}")

        view = next(
            (
                x for x in data
                if int(x["service"])
                == settings["view_service"]
            ),
            None,
        )

        reaction = next(
            (
                x for x in data
                if int(x["service"])
                == settings["reaction_service"]
            ),
            None,
        )

        if view:
            print(f"✅ View Service: {view['name']}")
        else:
            print(
                f"❌ View Service ({settings['view_service']}) Not Found"
            )

        if reaction:
            print(f"✅ Reaction Service: {reaction['name']}")
        else:
            print(
                f"❌ Reaction Service ({settings['reaction_service']}) Not Found"
            )

    except Exception as e:

        print("❌ CheapestSMM Connection Failed")
        print(e)


async def worker_loop():

    while True:

        try:
            # Pass bot to worker
            await worker(bot)

        except Exception as e:

            print(f"❌ Worker crashed: {e}")

            await asyncio.sleep(5)


async def main():

    await startup()

    for router in routers:
        dp.include_router(router)

    # Start worker in background
    asyncio.create_task(worker_loop())

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == "__main__":
    asyncio.run(main())