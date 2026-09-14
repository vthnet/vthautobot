from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InputMediaPhoto,
)
from utils import edit_or_send
import ui

from config import REFERRAL_REWARD
from database import (
    get_user,
    create_user,
    update_user,
    add_credits,
    add_history,
    get_bot_settings,
)
from database import get_balance
from database import get_history
from logger import log
from utils import joined
from database import get_bot_settings
router = Router()


async def reward_referral(bot, user_id: int, user, event_date):

    if user.get("joined"):
        return

    await update_user(
        user_id,
        {
            "joined": True,
            "last_active": event_date,
        }
    )

    ref = user.get("referred_by")

    if (
        not ref
        or ref == user_id
        or user.get("ref_rewarded")
    ):
        return

    ref_user = await get_user(ref)

    if not ref_user:
        return

    await add_credits(ref, REFERRAL_REWARD)
    await add_history(
         ref,
         REFERRAL_REWARD,
         f"Referral Reward (User {user_id})",
         "referral",
)
    await add_credits(user_id, REFERRAL_REWARD)
    await add_history(
          user_id,
          REFERRAL_REWARD,
          f"Joined via Referral ({ref})",
          "referral",
)
    await log(
        bot,
        "💰 Referral Credits Added",
        f"""
-------------------------------------------------------
👤 Referrer: <code>{ref}</code>
👤 New User: <code>{user_id}</code>
🎁 Reward:{REFERRAL_REWARD} Credits Each
-------------------------------------------------------
"""
    )

    await update_user(
        user_id,
        {"ref_rewarded": True}
    )

    try:
        await bot.send_message(
            ref,
            f"🎉 You earned <b>{REFERRAL_REWARD} Credits</b> from a successful referral!",
            parse_mode="HTML"
        )
    except:
        pass

    try:
        await bot.send_message(
            user_id,
            f"🎉 You received <b>{REFERRAL_REWARD} Credits</b> for joining through a referral!",
            parse_mode="HTML"
        )
    except:
        pass

    await log(
        bot,
        "🎁 Referral Reward",
        f"""
•Referrer:<code>{ref}</code>
•New User:<code>{user_id}</code>
•Reward: {REFERRAL_REWARD} Credits Each
"""
    )


@router.message(CommandStart())
async def start(message: Message):

    user = await get_user(message.from_user.id)

    if not user:

        ref = None

        args = message.text.split(maxsplit=1)

        if len(args) > 1:
            try:
                ref = int(args[1])
            except ValueError:
                pass

        if ref == message.from_user.id:
            ref = None

        await create_user(
            {
                "_id": message.from_user.id,
                "name": message.from_user.full_name,
                "username": message.from_user.username,
                "credits": 0,
                "channels": [],
                "referred_by": ref,
                "ref_rewarded": False,
                "joined": False,
                "created_at": message.date,
                "last_active": message.date,
            }
        )

        user = await get_user(message.from_user.id)

        await log(
            message.bot,
            "🆕 New User",
            f"""
👤 <b>{message.from_user.full_name}</b>
🆔 <code>{message.from_user.id}</code>
👤 @{message.from_user.username or 'None'}
🔗 Referrer: <code>{ref or 'None'}</code>
"""
        )

    # Force Join
    if not await joined(message.bot, message.from_user.id):
        return await message.answer(
            "🚫 <b>You must join our updates channel first.</b>",
            reply_markup=ui.force_join_keyboard(),
            parse_mode="HTML",
        )

    # Referral Reward
    await reward_referral(
        message.bot,
        message.from_user.id,
        user,
        message.date,
    )

    # Welcome Screen
    settings = await get_bot_settings()

    welcome_text = settings.get(
        "start_text",
        f"""
👋 <b>Welcome {message.from_user.first_name}</b>

<b>• Welcome to VTH AUTO BOT •</b>
<blockquote>🚀 Boost your Telegram channel with real Post Views & Reactions.

💎 Earn free Credits by inviting friends.

💳 Purchase Credits anytime to enable automatic boosting.

👇 Use the buttons below to get started.</blockquote>
<b>Fast • Secure • Reliable</b>
"""
    )

    start_photo = settings.get("start_photo")

    if start_photo:

        await message.answer_photo(
            photo=start_photo,
            caption=welcome_text,
            reply_markup=ui.home_keyboard(),
            parse_mode="HTML",
        )

    else:

        await message.answer(
            welcome_text,
            reply_markup=ui.home_keyboard(),
            parse_mode="HTML",
        )
      


@router.callback_query(F.data == "verify_join")
async def verify_join(call: CallbackQuery):

    if not await joined(call.bot, call.from_user.id):
        return await call.answer(
            "❌ Join the channel first.",
            show_alert=True,
        )

    user = await get_user(call.from_user.id)

    if user:
        await reward_referral(
            call.bot,
            call.from_user.id,
            user,
            call.message.date,
        )

    settings = await get_bot_settings()

    welcome_text = settings.get(
        "start_text",
        f"""
👋 <b>Welcome {call.from_user.first_name}</b>

<b>• Welcome to VTH AUTO BOT •</b>

<blockquote>
🚀 Boost your Telegram channel with real Post Views & Reactions.

💎 Earn free Credits by inviting friends.

💳 Purchase Credits anytime to enable automatic boosting.

👇 Use the buttons below to get started.
</blockquote>

<b>Fast • Secure •Reliable</b>
"""
    )

    photo = settings.get("start_photo")

    if photo:

        try:

            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=photo,
                    caption=welcome_text,
                    parse_mode="HTML",
                ),
                reply_markup=ui.home_keyboard(),
            )

        except Exception:

            await call.message.answer_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=ui.home_keyboard(),
                parse_mode="HTML",
            )

    else:

        await call.message.edit_text(
            welcome_text,
            reply_markup=ui.home_keyboard(),
            parse_mode="HTML",
        )

    await call.answer()


@router.callback_query(F.data == "home")
async def home(call: CallbackQuery):

    settings = await get_bot_settings()

    welcome_text = settings.get(
        "start_text",
        f"""
👋 <b>Welcome {call.from_user.first_name}</b>

• Welcome to VTH AUTO BOT •
"""
    )

    await edit_or_send(
        call,
        welcome_text,
        ui.home_keyboard(),
    )

    await call.answer()


@router.callback_query(F.data == "guide")
async def guide(call: CallbackQuery):

    await edit_or_send(
    call,
    """
📖 <b>How To Use</b>
--------------------------------------------------
Watch our complete guide below.
--------------------------------------------------
""",
    ui.guide_keyboard(),
)

    await call.answer()


@router.callback_query(F.data == "support")
async def support(call: CallbackQuery):

    await edit_or_send(
    call,
    """
🛟 <b>Support</b>
--------------------------------------------------
If you need help, contact:@vthnetsupport
--------------------------------------------------
""",
    ui.support_keyboard(),
)

    await call.answer()


@router.callback_query(F.data == "wallet")
async def wallet(call: CallbackQuery):

    balance = await get_balance(call.from_user.id)

    history = await get_history(call.from_user.id, 5)

    if history:

        recent = "\n".join(
            f"• {item['reason']} ({item['amount']:+})"
            for item in history
        )

    else:

        recent = "No transactions yet."

    await edit_or_send(
        call,
        f"""
💳 <b>Your Wallet</b>
--------------------------------------------------
💰 Balance :<b>{balance:,} Credits</b>
--------------------------------------------------
Purchase more credits or view your history below.
""",
        ui.wallet_keyboard(),
    )

    await call.answer()