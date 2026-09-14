from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from utils import edit_or_send
import ui

from database import (
    get_user,
    get_channel,
    get_channels,
    add_channel,
    delete_channel,
    update_channel,
    update_user,
    create_order,
)

router = Router()


class AddChannel(StatesGroup):
    waiting_channel = State()


class ChannelSettings(StatesGroup):
    waiting_views = State()
    waiting_reactions = State()


# ======================================================
# CHANNEL LIST
# ======================================================

@router.callback_query(F.data == "channels")
async def channels(call: CallbackQuery):

    channels = await get_channels(call.from_user.id)

    await edit_or_send(
        call,
        "📢 <b>My Channels</b>",
        ui.channels_keyboard(channels),
    )

    await call.answer()


# ======================================================
# ADD CHANNEL
# ======================================================

@router.callback_query(F.data == "add_channel")
async def add(call: CallbackQuery, state: FSMContext):

    await state.set_state(AddChannel.waiting_channel)

    await edit_or_send(
    call,
        """
📢 <b>Add Channel</b>
-------------------------------------------------------
•Forward any post from your channel
OR
•Send your channel username
•Example: @mychannel
-------------------------------------------------------
""",
        ui.cancel_keyboard(),
    )

    await call.answer()


@router.message(AddChannel.waiting_channel)
async def receive_channel(message: Message, state: FSMContext):

    chat = None

    if message.forward_from_chat:
        chat = message.forward_from_chat

    elif message.text and message.text.startswith("@"):

        try:
            chat = await message.bot.get_chat(message.text)
        except TelegramBadRequest:
            pass

    if not chat:

        return await message.answer(
            "❌ Invalid channel.\n\nForward a post or send @username."
        )

    try:

        member = await message.bot.get_chat_member(
            chat.id,
            message.bot.id,
        )

        if member.status != "administrator":

            return await message.answer(
                "❌ Add me as administrator first."
            )

    except TelegramBadRequest:

        return await message.answer(
            "❌ I couldn't verify the channel."
        )

    owner = await get_user(message.from_user.id)

    channels = owner.get("channels", [])

    if chat.id in channels:

        await state.clear()

        return await message.answer(
            "⚠️ Channel already added.",
            reply_markup=ui.home_keyboard(),
        )

    await add_channel(
        {
            "_id": chat.id,
            "owner": message.from_user.id,
            "title": chat.title,
            "username": chat.username,
            "auto": False,

            "views": 100,
            "reactions": 0,

            "last_post": 0,

            "posts_boosted": 0,
            "views_sent": 0,
            "reactions_sent": 0,
            "credits_used": 0,
        }
    )

    channels.append(chat.id)

    await update_user(
        message.from_user.id,
        {"channels": channels},
    )

    await state.clear()

    try:

        await message.bot.send_message(
            message.from_user.id,
            f"""
✅ <b>Channel Added Successfully</b>
-------------------------------------------------------
📢 <b>{chat.title}</b>
🤖 Auto Mode
🔴 OFF
-------------------------------------------------------
Configure Views & Reactions from <b>My Channels</b>.
""",
            parse_mode="HTML",
        )

    except Exception:
        pass

    await message.answer(
    f"""
📢 <b>{chat.title}</b>
--------------------------------------------------
<blockquote>🤖 Auto Mode : 🔴 OFF
👀 Auto Views : 100
❤️ Auto Reactions : 0
--------------------------------------------------</blockquote>
Configure your channel below.
""",
    reply_markup=ui.channel_keyboard(chat.id),
    parse_mode="HTML",
)


# ======================================================
# AUTO VIEWS
# ======================================================

@router.callback_query(F.data.startswith("views_"))
async def edit_views(call: CallbackQuery, state: FSMContext):

    chat_id = int(call.data.split("_")[1])

    await state.update_data(
    chat_id=chat_id,
    bot_message=call.message.message_id,
)

    await state.set_state(ChannelSettings.waiting_views)

    await edit_or_send(
    call,
        """
👀 <b>Auto Views</b>
-------------------------------------------------------
•Send number of views.

0 = Disable
20 - 9000 = Enable
-------------------------------------------------------
""",
        ui.cancel_keyboard(),
    )

    await call.answer()


@router.message(ChannelSettings.waiting_views)
async def save_views(message: Message, state: FSMContext):

    if not message.text or not message.text.isdigit():
        return await message.answer(
            "❌ Send numbers only."
        )

    amount = int(message.text)

    if amount != 0 and not (20 <= amount <= 9000):
        return await message.answer(
            "❌ Views must be between 20-9000."
        )

    data = await state.get_data()

    await update_channel(
        data["chat_id"],
        {
            "views": amount
        },
    )

    try:
        await message.delete()
    except Exception:
        pass

    bot_message = data["bot_message"]

    try:

        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=bot_message,
            caption=f"""
✅ <b>Auto Views Updated</b>
--------------------------------------------------
👀 Views :<b>{amount}</b>
--------------------------------------------------
Every new post will receive this amount automatically.
""",
            parse_mode="HTML",
            reply_markup=ui.back_home_keyboard(
                data["chat_id"]
            ),
        )

    except Exception:

        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message,
            text=f"""
✅ <b>Auto Views Updated</b>
--------------------------------------------------
👀 Views :<b>{amount}</b>
--------------------------------------------------
Every new post will receive this amount automatically.
""",
            parse_mode="HTML",
            reply_markup=ui.back_home_keyboard(
                data["chat_id"]
            ),
        )
    await state.clear()

# ======================================================
# AUTO REACTIONS
# ======================================================

@router.callback_query(F.data.startswith("reactions_"))
async def edit_reactions(call: CallbackQuery, state: FSMContext):

    chat_id = int(call.data.split("_")[1])

    await state.update_data(
    chat_id=chat_id,
    bot_message=call.message.message_id,
)

    await state.set_state(ChannelSettings.waiting_reactions)

    await edit_or_send(
    call,
        """
❤️ <b>Auto Reactions</b>
-------------------------------------------------------
•Send number of reactions.

0 = Disable
20 - 5000 = Enable
-------------------------------------------------------
""",
        ui.cancel_keyboard(),
    )

    await call.answer()


@router.message(ChannelSettings.waiting_reactions)
async def save_reactions(message: Message, state: FSMContext):

    if not message.text or not message.text.isdigit():
        return await message.answer(
            "❌ Send numbers only."
        )

    amount = int(message.text)

    if amount != 0 and not (20 <= amount <= 5000):
        return await message.answer(
            "❌ Reactions must be between 20-5000."
        )

    data = await state.get_data()

    await update_channel(
        data["chat_id"],
        {
            "reactions": amount
        },
    )

    try:
        await message.delete()
    except Exception:
        pass

    bot_message = data["bot_message"]

    try:

        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=bot_message,
            caption=f"""
✅ <b>Auto Reactions Updated</b>
--------------------------------------------------
❤️ Reactions :<b>{amount}</b>
--------------------------------------------------

Every new post will receive this amount automatically.
""",
            parse_mode="HTML",
            reply_markup=ui.back_home_keyboard(
                data["chat_id"]
            ),
        )

    except Exception:

        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message,
            text=f"""
✅ <b>Auto Reactions Updated</b>
--------------------------------------------------
❤️ Reactions :<b>{amount}</b>
--------------------------------------------------
Every new post will receive this amount automatically.
""",
            parse_mode="HTML",
            reply_markup=ui.back_home_keyboard(
                data["chat_id"]
            ),
        )

    await state.clear()


# ======================================================
# CHANNEL DETAILS
# ======================================================

@router.callback_query(F.data.startswith("channel_"))
async def channel(call: CallbackQuery):

    chat_id = int(call.data.split("_")[1])

    channel = await get_channel(chat_id)

    if not channel:
        return await call.answer(
            "Channel not found.",
            show_alert=True,
        )

    status = "🟢 ON" if channel.get("auto") else "🔴 OFF"

    await edit_or_send(
    call,
        f"""
📢 <b>{channel['title']}</b>
<blockquote>-------------------------------------------------------
🤖 <b>Auto Mode</b> :{status}

👀 <b>Auto Views</b> :{channel.get("views", 0)}
❤️ <b>Auto Reactions</b> :{channel.get("reactions", 0)}

📨 <b>Posts Boosted</b> :{channel.get("posts_boosted", 0)}
👀 <b>Total Views Sent</b> :{channel.get("views_sent", 0):,}
❤️ <b>Total Reactions Sent</b> :{channel.get("reactions_sent", 0):,}

💰 <b>Credits Used</b> :{channel.get("credits_used", 0):,}
-------------------------------------------------------</blockquote>
""",
        ui.channel_keyboard(chat_id),
    )

    await call.answer()


# ======================================================
# TOGGLE AUTO MODE
# ======================================================

@router.callback_query(F.data.startswith("toggle_"))
async def toggle(call: CallbackQuery):

    chat_id = int(call.data.split("_")[1])

    channel_data = await get_channel(chat_id)

    if not channel_data:
        return await call.answer()

    auto = not channel_data["auto"]

    await update_channel(
        chat_id,
        {
            "auto": auto
        },
    )


    await call.answer(
        f"Auto Mode {'Enabled' if auto else 'Disabled'}",
        show_alert=True,
    )

    await channel(call)


# ======================================================
# DELETE CHANNEL
# ======================================================

@router.callback_query(F.data.startswith("delete_"))
async def remove(call: CallbackQuery):

    chat_id = int(call.data.split("_")[1])

    user = await get_user(call.from_user.id)

    channels = user.get("channels", [])

    if chat_id in channels:

        channels.remove(chat_id)

        await update_user(
            call.from_user.id,
            {
                "channels": channels
            },
        )

    channel_data = await get_channel(chat_id)

    await delete_channel(chat_id)

    try:

        await call.bot.send_message(
            call.from_user.id,
            f"""
🗑 <b>Channel Removed</b>
--------------------------------------------------
📢 {channel_data['title'] if channel_data else chat_id}
--------------------------------------------------
The channel has been removed successfully.
""",
            parse_mode="HTML",
        )

    except Exception:
        pass

    await edit_or_send(
    call,
        "✅ Channel removed successfully.",
        ui.home_keyboard(),
    )

    await call.answer()


# ======================================================
# NEW POST DETECTED
# ======================================================

@router.channel_post()
async def new_post(post: Message):

    channel = await get_channel(post.chat.id)

    if not channel:
        return

    if not channel.get("auto"):
        return

    if post.message_id <= channel.get("last_post", 0):
        return

    await update_channel(
        post.chat.id,
        {
            "last_post": post.message_id
        }
    )

    views = channel.get("views", 0)
    reactions = channel.get("reactions", 0)

    # Nothing to boost
    if views == 0 and reactions == 0:
        return

    post_link = (
        f"https://t.me/{channel['username']}/{post.message_id}"
        if channel.get("username")
        else "Private Channel"
    )

    # Create pending order
    await create_order(
        {
            "chat_id": post.chat.id,
            "message_id": post.message_id,

            "owner": channel["owner"],

            "views": views,
            "reactions": reactions,

            "status": "pending",

            "view_order": None,
            "reaction_order": None,
        }
    )

    # Notify user
    try:

        await post.bot.send_message(
            channel["owner"],
            f"""
📝 <b>New Post Detected</b>
<blockquote>-------------------------------------------------------
📢 <b>Channel</b> :{channel['title']}
🔗 <b>Post</b> :{post_link}
👀 <b>Views Requested</b> :{views}
❤️ <b>Reactions Requested</b> :{reactions}
-------------------------------------------------------</blockquote>
⏳ Status
Waiting for worker...
Your boost request has been queued successfully.
""",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    except Exception as e:
        print(f"New Post Notification Error: {e}")

    print(
        f"📝 New Post Queued | "
        f"{channel['title']} | "
        f"{post.message_id}"
    )