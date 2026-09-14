from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import ui

from config import OWNER_ID
from database import (
    get_settings,
    update_settings,
)

router = Router()


SETTINGS = {
    "set_views_per_credit": (
        "views_per_credit",
        int,
        "👀 Views / Credit"
    ),
    "set_reactions_per_credit": (
        "reactions_per_credit",
        int,
        "❤️ Reactions / Credit"
    ),
    "set_referral": (
        "referral_reward",
        int,
        "🎁 Referral Reward"
    ),
    "set_rupee": (
        "credits_per_rupee",
        int,
        "💰 Credits per ₹"
    ),
    "set_min_views": (
        "min_views",
        int,
        "👀 Minimum Views"
    ),
    "set_max_views": (
        "max_views",
        int,
        "👀 Maximum Views"
    ),
    "set_min_reactions": (
        "min_reactions",
        int,
        "❤️ Minimum Reactions"
    ),
    "set_max_reactions": (
        "max_reactions",
        int,
        "❤️ Maximum Reactions"
    ),
    "set_force_join": (
        "force_join",
        str,
        "📢 Force Join Channel"
    ),
    "set_view_service": (
        "view_service",
        int,
        "🆔 View Service ID"
    ),
    "set_reaction_service": (
        "reaction_service",
        int,
        "🆔 Reaction Service ID"
    ),
}


class EditSetting(StatesGroup):
    waiting_value = State()


def build_text(data: dict):

    return f"""
⚙ <b>Bot Settings</b>
-------------------------------------------------------
👀 Views / Credit :<b>{data['views_per_credit']}</b>
❤️ Reactions / Credit :<b>{data['reactions_per_credit']}</b>
🎁 Referral Reward :<b>{data['referral_reward']}</b>
💰 Credits/₹ :<b>{data['credits_per_rupee']}</b>
👀 Views :<b>{data['min_views']} - {data['max_views']}</b>
❤️ Reactions :<b>{data['min_reactions']} - {data['max_reactions']}</b>
📢 Force Join :<b>{data['force_join']}</b>
🆔 View Service :<b>{data['view_service']}</b>
🆔 Reaction Service :<b>{data['reaction_service']}</b>
-------------------------------------------------------
"""


@router.callback_query(F.data == "admin_settings")
async def admin_settings(call: CallbackQuery):

    if call.from_user.id != OWNER_ID:
        return await call.answer()

    data = await get_settings()

    await call.message.edit_text(
        build_text(data),
        reply_markup=ui.settings_keyboard(),
        parse_mode="HTML",
    )

    await call.answer()

@router.callback_query(F.data.in_(SETTINGS.keys()))
async def edit_setting(call: CallbackQuery, state: FSMContext):

    if call.from_user.id != OWNER_ID:
        return await call.answer()

    data = await get_settings()

    field, value_type, title = SETTINGS[call.data]

    await state.update_data(
        field=field,
        value_type=value_type.__name__,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )

    await state.set_state(EditSetting.waiting_value)

    await call.message.edit_text(
        f"""
{title}

Current Value

<b>{data[field]}</b>

Send new value.
""",
        reply_markup=ui.cancel_keyboard(),
        parse_mode="HTML"
    )

    await call.answer()


@router.message(EditSetting.waiting_value)
async def save_setting(message: Message, state: FSMContext):

    if message.from_user.id != OWNER_ID:
        return

    state_data = await state.get_data()

    field = state_data["field"]
    value_type = state_data["value_type"]

    value = message.text.strip()

    if value_type == "int":

        if not value.isdigit():
            return await message.answer(
                "❌ Please send numbers only."
            )

        value = int(value)

    await update_settings(
        {
            field: value
        }
    )

    settings = await get_settings()

    chat_id = state_data["chat_id"]
    message_id = state_data["message_id"]

    await state.clear()

    try:

        await message.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=build_text(settings),
            reply_markup=ui.settings_keyboard(),
            parse_mode="HTML",
        )

        await message.answer(
            "✅ Setting updated successfully."
        )

    except Exception:

        await message.answer(
            "✅ Setting updated successfully."
        )

        await message.answer(
            build_text(settings),
            reply_markup=ui.settings_keyboard(),
            parse_mode="HTML",
        )