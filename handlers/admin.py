from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from logger import log
import ui
from config import OWNER_ID
from database import (
    users,
    channels,
    payments,
    orders,
    get_payment,
    update_payment,
    add_credits,
    resume_orders,
    add_history,
    update_bot_settings,
)

router = Router()

class Broadcast(StatesGroup):
    waiting_message = State()


class SettingsState(StatesGroup):
    waiting_value = State()


class BotSettingsState(StatesGroup):
    waiting_start_photo = State()
    waiting_start_text = State()


def is_admin(user_id: int):
    return user_id == OWNER_ID


@router.callback_query(F.data == "admin")
async def admin_panel(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return await call.answer(
            "Access Denied",
            show_alert=True
        )

    total_users = await users.count_documents({})
    total_channels = await channels.count_documents({})
    pending = await payments.count_documents(
        {"status": "pending"}
    )

    await call.message.edit_text(
        f"""
👑 <b>Admin Panel</b>

👥 Users
<b>{total_users}</b>

📢 Channels
<b>{total_channels}</b>

💳 Pending Payments
<b>{pending}</b>
""",
        reply_markup=ui.admin_keyboard(),
        parse_mode="HTML"
    )

    await call.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    total_users = await users.count_documents({})

    total_channels = await channels.count_documents({})

    pending_payments = await payments.count_documents(
        {"status": "pending"}
    )

    approved_payments = await payments.count_documents(
        {"status": "approved"}
    )

    payment_data = await payments.aggregate([
        {
            "$match": {
                "status": "approved"
            }
        },
        {
            "$group": {
                "_id": None,
                "amount": {
                    "$sum": "$amount"
                },
                "credits": {
                    "$sum": "$credits"
                }
            }
        }
    ]).to_list(1)

    order_data = await orders.aggregate([
        {
            "$group": {
                "_id": None,
                "credits_used": {
                    "$sum": "$credits_used"
                }
            }
        }
    ]).to_list(1)

    completed = await orders.count_documents(
        {"status": "completed"}
    )

    paused = await orders.count_documents(
        {"status": "paused"}
    )

    failed = await orders.count_documents(
        {"status": "failed"}
    )

    total_revenue = (
        payment_data[0]["amount"]
        if payment_data else 0
    )

    credits_sold = (
        payment_data[0]["credits"]
        if payment_data else 0
    )

    credits_used = (
        order_data[0]["credits_used"]
        if order_data else 0
    )

    await call.message.edit_text(
        f"""
📊 <b>Revenue Dashboard</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 Users :<b>{total_users:,}</b>
📢 Channels :<b>{total_channels:,}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Revenue :₹<b>{total_revenue:,}</b>
💳 Approved Payments :<b>{approved_payments:,}</b>
⏳ Pending Payments :<b>{pending_payments:,}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
🎁 Credits Sold :<b>{credits_sold:,}</b>
💸 Credits Used :<b>{credits_used:,}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Completed Orders :<b>{completed:,}</b>
⏸ Paused Orders :<b>{paused:,}</b>
❌ Failed Orders :<b>{failed:,}</b>
""",
        reply_markup=ui.admin_keyboard(),
        parse_mode="HTML",
    )

    await call.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    total = await users.count_documents({})

    await call.answer(
        f"Users : {total}",
        show_alert=True
    )


@router.callback_query(F.data == "admin_channels")
async def admin_channels(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    total = await channels.count_documents({})

    await call.answer(
        f"Channels : {total}",
        show_alert=True
    )


@router.callback_query(F.data == "admin_payments")
async def admin_payments(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    pending = await payments.find(
        {"status": "pending"}
    ).to_list(10)

    if not pending:

        return await call.answer(
            "No pending payments.",
            show_alert=True
        )

    payment = pending[0]

    await call.message.edit_text(
        f"""
💳 <b>Pending Payment</b>

👤 User
<code>{payment['user_id']}</code>

💵 Amount
₹{payment['amount']}

🎁 Credits
{payment['credits']}
""",
        reply_markup=ui.payment_keyboard(
            payment["_id"]
        ),
        parse_mode="HTML"
    )

    await call.answer()



@router.callback_query(F.data.startswith("approve_"))
async def approve_payment(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return
    payment_id = call.data.split("_", 1)[1]
    payment = await get_payment(payment_id)
    if not payment:
        return await call.answer(
            "Payment not found.",
            show_alert=True
        )
    if payment["status"] != "pending":
        return await call.answer(
            "Already processed.",
            show_alert=True
        )
    await add_credits(
    payment["user_id"],
    payment["credits"]
)
    await add_history(
    payment["user_id"],
    payment["credits"],
    f"Recharge ₹{payment['amount']}",
    "recharge",
    )

    await resume_orders(
    payment["user_id"]
    )
      
    try:
       await call.bot.send_message(
        payment["user_id"],
        """
🔄 <b>Your paused boost orders have resumed.</b>

Thank you for recharging your wallet.
""",
        parse_mode="HTML",
    )
    except Exception:
      pass
  
    await update_payment(
        payment_id,
        {
            "status": "approved",
            "approved_by": call.from_user.id,
        }
    )
    try:

        await call.bot.send_message(
        payment["user_id"],
        f"""
🎉 <b>Recharge Successful</b>
━━━━━━━━━━━━━━
💰 Credits Added :<b>{payment['credits']}</b>
💳 Amount Paid :₹{payment['amount']}
━━━━━━━━━━━━━━
Your wallet has been updated.
Thank you for choosing VTH AUTO BOT ❤️
""",
        parse_mode="HTML",
    )
    except Exception:
      pass


    await call.message.edit_caption(
        call.message.caption + "\n\n✅ APPROVED",
        reply_markup=None
    )
    await call.answer("Approved")
    await log(
         call.bot,
    "Recharge Approved",
    f"""
👤 <code>{payment['user_id']}</code>

💰 Credits
{payment['credits']}

💵 Amount
₹{payment['amount']}
""",
    "💳",
)


@router.callback_query(F.data.startswith("reject_"))
async def reject_payment(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return

    payment_id = call.data.split("_", 1)[1]

    payment = await get_payment(payment_id)

    if not payment:
        return

    if payment["status"] != "pending":
        return

    await update_payment(
        payment_id,
        {
            "status": "rejected",
            "rejected_by": call.from_user.id,
        }
    )

    try:

        await call.bot.send_message(
        payment["user_id"],
        f"""
❌ <b>Payment Rejected</b>

Unfortunately your payment could not be verified.

If you think this is a mistake, please contact

👤 @vthnetsupport
""",
        parse_mode="HTML",
    )

    except Exception:
          pass

    await call.message.edit_caption(
        call.message.caption + "\n\n❌ REJECTED",
        reply_markup=None
    )

    await call.answer("Rejected")
    await log(
    call.bot,
    "Recharge Rejected",
    f"""
👤 <code>{payment['user_id']}</code>

💵 Amount
₹{payment['amount']}
""",
    "❌",
)



@router.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id != OWNER_ID:
        return

    await message.answer(
        "👑 <b>Admin Panel</b>",
        reply_markup=ui.admin_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("setstartphoto"))
async def set_start_photo(message: Message, state: FSMContext):

    if message.from_user.id != OWNER_ID:
        return

    await state.set_state(BotSettingsState.waiting_start_photo)

    await message.answer(
        "📸 Send the photo you want to use as the bot welcome image."
    )

@router.message(BotSettingsState.waiting_start_photo)
async def save_start_photo(message: Message, state: FSMContext):

    if not message.photo:
        return await message.answer("Please send a photo.")

    await update_bot_settings(
        {
            "start_photo": message.photo[-1].file_id
        }
    )

    await state.clear()

    await message.answer(
        "✅ Welcome image updated."
    )

@router.message(Command("setstarttext"))
async def set_start_text(message: Message, state: FSMContext):

    if message.from_user.id != OWNER_ID:
        return
    await state.set_state(
        BotSettingsState.waiting_start_text
    )
    await message.answer(
        "Send the new welcome message."
    )


@router.message(BotSettingsState.waiting_start_text)
async def save_start_text(message: Message, state: FSMContext):
    await update_bot_settings(
        {
            "start_text": message.html_text
        }
    )
    await state.clear()

    await message.answer(
        "✅ Welcome text updated."
    )