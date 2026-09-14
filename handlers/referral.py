from aiogram import Router, F
from aiogram.types import CallbackQuery

import ui

from config import REFERRAL_REWARD, BOT_USERNAME
from database import get_balance
from utils import edit_or_send

router = Router()


@router.callback_query(F.data == "refer")
async def referral(call: CallbackQuery):

    balance = await get_balance(call.from_user.id)

    link = f"https://t.me/{BOT_USERNAME}?start={call.from_user.id}"

    await edit_or_send(
        call,
        f"""
🎁 <b>Refer & Earn</b>
•Invite your friends using your personal referral link.
<blockquote>--------------------------------------------------
🎉 <b>Reward</b>
• You receive <b>{REFERRAL_REWARD} Credits</b>
• Your friend receives <b>{REFERRAL_REWARD} Credits</b>
--------------------------------------------------
💰 <b>Your Balance</b>
<b>{balance:,} Credits</b>
--------------------------------------------------</blockquote>
your link🔗 : <code>{link}</code>
""",
        ui.referral_keyboard(),
    )

    await call.answer()