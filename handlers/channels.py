from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from html import escape
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
    get_settings,
    get_balance,
    calculate_order_credits,
)

router = Router()


class AddChannel(StatesGroup):
    waiting_channel = State()


class ChannelSettings(StatesGroup):
    waiting_views = State()
    waiting_reactions = State()


def _rate_preview(views: int, reactions: int, settings: dict, balance: int) -> str:
    view_credits, reaction_credits, total_credits = calculate_order_credits(
        views, reactions, settings
    )

    credits_per_rupee = max(1, int(settings.get("credits_per_rupee", 50)))
    rupee_equivalent = total_credits / credits_per_rupee
    remaining = max(0, int(balance) - total_credits)

    return f"""
💳 <b>Credit Usage Preview</b>
• 👀 {int(views):,} views → <b>{view_credits:,} credits</b>
• ❤️ {int(reactions):,} reactions → <b>{reaction_credits:,} credits</b>

📊 <b>Total per post</b> → <b>{total_credits:,} credits</b>
💵 Approx. value → <b>₹{rupee_equivalent:.2f}</b>
💰 Current balance → <b>{int(balance):,} credits</b>
📉 Balance after one post → <b>{remaining:,} credits</b>
"""


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
    settings = await get_settings()
    channel = await get_channel(data["chat_id"])
    current_reactions = int(channel.get("reactions", 0)) if channel else 0
    balance = await get_balance(message.from_user.id)

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
    preview = _rate_preview(amount, current_reactions, settings, balance)

    text = f"""
✅ <b>Auto Views Updated</b>
--------------------------------------------------
👀 Views : <b>{amount:,}</b>
❤️ Reactions : <b>{current_reactions:,}</b>
--------------------------------------------------
{preview}
--------------------------------------------------
Every new post will use this conversion automatically.
No credits are deducted now.
"""

    try:
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=bot_message,
            caption=text,
            parse_mode="HTML",
            reply_markup=ui.back_home_keyboard(
                data["chat_id"]
            ),
        )

    except Exception:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message,
            text=text,
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
    settings = await get_settings()
    channel = await get_channel(data["chat_id"])
    current_views = int(channel.get("views", 0)) if channel else 0
    balance = await get_balance(message.from_user.id)

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
    preview = _rate_preview(current_views, amount, settings, balance)

    text = f"""
✅ <b>Auto Reactions Updated</b>
--------------------------------------------------
👀 Views : <b>{current_views:,}</b>
❤️ Reactions : <b>{amount:,}</b>
--------------------------------------------------
{preview}
--------------------------------------------------
Every new post will use this conversion automatically.
No credits are deducted now.
"""

    try:
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=bot_message,
            caption=text,
            parse_mode="HTML",
            reply_markup=ui.back_home_keyboard(
                data["chat_id"]
            ),
        )

    except Exception:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message,
            text=text,
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
    settings = await get_settings()
    balance = await get_balance(call.from_user.id)
    preview = _rate_preview(
        int(channel.get("views", 0)),
        int(channel.get("reactions", 0)),
        settings,
        balance,
    )

    await edit_or_send(
    call,
        f"""
📢 <b>{escape(channel.get('title') or 'Unknown Channel')}</b>
<blockquote>-------------------------------------------------------
🤖 <b>Auto Mode</b> :{status}

👀 <b>Auto Views</b> :{channel.get("views", 0):,}
❤️ <b>Auto Reactions</b> :{channel.get("reactions", 0):,}

{preview}

📨 <b>Posts Boosted</b> :{channel.get("posts_boosted", 0):,}
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
📢 {escape(channel_data.get('title') if channel_data else str(chat_id))}
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

    # Ignore Telegram service/system messages. These are not real channel posts
    # and must never advance last_post or create an order.
    service_fields = (
        "pinned_message",
        "new_chat_members",
        "left_chat_member",
        "new_chat_title",
        "new_chat_photo",
        "delete_chat_photo",
        "group_chat_created",
        "supergroup_chat_created",
        "channel_chat_created",
        "migrate_to_chat_id",
        "migrate_from_chat_id",
        "video_chat_started",
        "video_chat_ended",
        "video_chat_participants_invited",
        "forum_topic_created",
        "forum_topic_closed",
        "forum_topic_reopened",
        "general_forum_topic_hidden",
        "general_forum_topic_unhidden",
    )

    if any(getattr(post, field, None) for field in service_fields):
        return

    # Telegram sends every item of an album as a separate channel_post update.
    # media_group_id makes all those messages share one logical post_key.
    media_group_id = getattr(post, "media_group_id", None)
    if media_group_id:
        post_key = f"{post.chat.id}:album:{media_group_id}"
    else:
        post_key = f"{post.chat.id}:message:{post.message_id}"

    if post.message_id <= channel.get("last_post", 0) and not media_group_id:
        return

    views = int(channel.get("views", 0))
    reactions = int(channel.get("reactions", 0))

    # Nothing to boost. Do not create a useless order.
    if views == 0 and reactions == 0:
        # Still advance last_post for real posts so an old post is not
        # repeatedly considered after auto mode is changed later.
        await update_channel(
            post.chat.id,
            {"last_post": max(post.message_id, channel.get("last_post", 0))}
        )
        return

    post_link = (
        f"https://t.me/{channel['username']}/{post.message_id}"
        if channel.get("username")
        else "Private Channel"
    )

    # MongoDB unique sparse index on post_key makes this atomic:
    # duplicate album items / duplicate updates can never create another order.
    created = await create_order(
        {
            "post_key": post_key,
            "media_group_id": media_group_id,
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

    if not created:
        return

    await update_channel(
        post.chat.id,
        {
            "last_post": max(post.message_id, channel.get("last_post", 0))
        }
    )

    # Notify user only once, after the order was actually inserted.
    try:
        await post.bot.send_message(
            channel["owner"],
            f"""
📝 <b>New Post Detected</b>
<blockquote>-------------------------------------------------------
📢 <b>Channel</b> :{escape(channel.get('title') or 'Unknown Channel')}
🔗 <b>Post</b> :{post_link}
👀 <b>Views Requested</b> :{views:,}
❤️ <b>Reactions Requested</b> :{reactions:,}
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
        f"{channel.get('title') or 'Unknown Channel'} | "
        f"{post.message_id}"
    )

