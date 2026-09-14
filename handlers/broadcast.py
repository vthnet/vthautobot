from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import asyncio
import time

from config import OWNER_ID
from database import users

router = Router()


@router.message(Command("broadcast"))
async def broadcast(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if not message.reply_to_message:

        return await message.reply(
            """
❌ <b>Reply to the message you want to broadcast.</b>

Example:

Reply to any message and send

<code>/broadcast</code>
""",
            parse_mode="HTML",
        )

    source = message.reply_to_message

    users_list = await users.find(
        {},
        {"_id": 1},
    ).to_list(None)

    total = len(users_list)

    sent = 0
    failed = 0

    start = time.time()

    status = await message.reply(
        f"""
📢 <b>Broadcast Started</b>

👥 Total Users
<b>{total}</b>

✅ Sent
<b>0</b>

❌ Failed
<b>0</b>
""",
        parse_mode="HTML",
    )

    for index, user in enumerate(users_list, start=1):

        try:

            await message.bot.copy_message(
                chat_id=user["_id"],
                from_chat_id=source.chat.id,
                message_id=source.message_id,
            )

            sent += 1

        except Exception:
            failed += 1

        if index % 100 == 0:

            try:

                await status.edit_text(
                    f"""
📢 <b>Broadcast Running...</b>

👥 Total
<b>{total}</b>

✅ Sent
<b>{sent}</b>

❌ Failed
<b>{failed}</b>

⏳ Remaining
<b>{total-index}</b>
""",
                    parse_mode="HTML",
                )

            except Exception:
                pass

        await asyncio.sleep(0.05)

    elapsed = round(time.time() - start, 2)

    await status.edit_text(
        f"""
✅ <b>Broadcast Finished</b>

━━━━━━━━━━━━━━

👥 Total Users
<b>{total}</b>

✅ Sent
<b>{sent}</b>

❌ Failed
<b>{failed}</b>

⏱ Time
<b>{elapsed} sec</b>
""",
        parse_mode="HTML",
    )