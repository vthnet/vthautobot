from aiogram import Bot
from datetime import datetime

from config import LOG_CHANNEL_ID


async def log(
    bot: Bot,
    title: str,
    text: str,
    emoji: str = "📌",
):

    if not LOG_CHANNEL_ID:
        return

    try:

        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"""
{emoji} <b>{title}</b>

━━━━━━━━━━━━━━━━━━

{text}

━━━━━━━━━━━━━━━━━━

🕒 <b>{datetime.now().strftime("%d %b %Y %H:%M:%S")}</b>
""",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    except Exception as e:
        print(f"❌ Logger Error: {e}")