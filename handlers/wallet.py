from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    FSInputFile,
    InputMediaPhoto,
)

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from datetime import datetime
import os

import ui

from config import OWNER_ID

from database import (
    get_balance,
    get_history,
    create_payment,
    get_settings,
)

router = Router()

QR_FILE = "assets/qr.jpg"

if not os.path.exists(QR_FILE):
    QR_FILE = "qr.jpg"


class Payment(StatesGroup):
    waiting_credits = State()
    waiting_screenshot = State()


async def edit_wallet_message(
    call: CallbackQuery,
    text: str,
    keyboard,
):
    try:

        if call.message.photo:

            await call.message.edit_caption(
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

        else:

            await call.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

    except Exception:

        if call.message.photo:

            await call.message.answer_photo(
                call.message.photo[-1].file_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

        else:

            await call.message.answer(
                text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )


@router.callback_query(F.data == "wallet")
async def wallet(
    call: CallbackQuery,
    state: FSMContext,
):

    await state.clear()

    balance = await get_balance(call.from_user.id)

    text = f"""
💳 <b>Your Wallet</b>
--------------------------------------------------

💰 Balance :<b>{balance:,} Credits</b>
--------------------------------------------------
"""

    await edit_wallet_message(
        call,
        text,
        ui.wallet_keyboard(),
    )

    await call.answer()


@router.callback_query(F.data == "buy")
async def buy(
    call: CallbackQuery,
    state: FSMContext,
):

    await state.clear()

    await state.set_state(
        Payment.waiting_credits
    )

    await state.update_data(
        bot_message=call.message.message_id
    )

    text = """
💳 <b>Buy Credits</b>
<blockquote>--------------------------------------------------
Send how many Credits you want.

•Minimum :<b>2,000 Credits</b>
•Amount : (₹20 / $0.20)
•Example :
<code>2000</code>
or
<code>5000</code>
--------------------------------------------------</blockquote>
"""

    await edit_wallet_message(
        call,
        text,
        ui.cancel_keyboard(),
    )

    await call.answer()


@router.message(Payment.waiting_credits)
async def receive_credit_amount(
    message: Message,
    state: FSMContext,
):

    if not message.text or not message.text.isdigit():
        return await message.answer(
            "❌ Please send numbers only."
        )

    credits = int(message.text)

    MIN_CREDITS = 2000

    if credits < MIN_CREDITS:
     return await message.answer(
        f"❌ Minimum purchase is {MIN_CREDITS:,} Credits (₹20 / $0.20)."
    )

    settings = await get_settings()

    credits_per_rupee = settings["credits_per_rupee"]

    rupees = round(
        credits / credits_per_rupee,
        2,
    )

    usd = round(
        rupees / 100,
        2,
    )

    data = await state.get_data()

    old_message = data.get("bot_message")

    await state.update_data(
        credits=credits,
        amount=rupees,
    )

    try:
        await message.delete()
    except Exception:
        pass

    photo = FSInputFile(QR_FILE)

    caption = f"""
💳 <b>Complete Your Payment</b>
--------------------------------------------------
🎁 Credits :<b>{credits:,}</b>
💵 INR :<b>₹{rupees}</b>
💲 USD :<b>${usd}</b>
--------------------------------------------------
(₹)UPI ID :<code>YOUR_UPI_ID</code>
($)Binance id :<code>922339798</code>
($)Cwallet id :<code>90779717</code>  
--------------------------------------------------
Scan the QR / pay using other methods and take ss .
"""

    # If we don't have a message id, send a fresh QR message.
    if old_message is None:

        sent = await message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=ui.payment_confirm_keyboard(),
        )

        await state.update_data(
            bot_message=sent.message_id,
        )

        return

    try:

        await message.bot.edit_message_media(
            chat_id=message.chat.id,
            message_id=old_message,
            media=InputMediaPhoto(
                media=photo,
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=ui.payment_confirm_keyboard(),
        )

        await state.update_data(
            bot_message=old_message,
        )

    except Exception as e:

        print("Wallet edit error:", e)

        sent = await message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=ui.payment_confirm_keyboard(),
        )

        await state.update_data(
            bot_message=sent.message_id,
        )


@router.callback_query(F.data == "payment_done")
async def payment_done(
    call: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(
        Payment.waiting_screenshot
    )

    await state.update_data(
        bot_message=call.message.message_id
    )

    text = """
📤 <b>Payment Verification</b>
--------------------------------------------------
•Please send your payment screenshot.
•Accepted Payments
✅ UPI (₹)
✅ Usdt ($)
--------------------------------------------------
Your credits will be added after manual verification.
"""

    await edit_wallet_message(
        call,
        text,
        ui.cancel_keyboard(),
    )

    await call.answer()


@router.message(Payment.waiting_screenshot)
async def receive_screenshot(
    message: Message,
    state: FSMContext,
):

    if not message.photo:
        return await message.answer(
            "❌ Please send a payment screenshot."
        )

    data = await state.get_data()

    try:
        await message.delete()
    except Exception:
        pass

    payment_id = await create_payment(
        {
            "user_id": message.from_user.id,
            "amount": data["amount"],
            "credits": data["credits"],
            "photo": message.photo[-1].file_id,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
    )

    await message.bot.send_photo(
        OWNER_ID,
        photo=message.photo[-1].file_id,
        caption=f"""
💳 <b>New Recharge Request</b>
--------------------------------------------------
👤 User :<code>{message.from_user.id}</code>
🎁 Credits :<b>{data['credits']}</b>
💵 Amount :₹{data['amount']}
--------------------------------------------------
Approve or Reject below.
""",
        parse_mode="HTML",
        reply_markup=ui.payment_keyboard(
            str(payment_id)
        ),
    )

    bot_message = data.get("bot_message")

    success_text = """
✅ <b>Payment Submitted</b>
--------------------------------------------------
•Your payment request has been submitted successfully.
•Please wait while our team verifies it.

•Need help?
👤Support : @vthnetsupport
--------------------------------------------------
"""

    if bot_message:

        try:

            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=bot_message,
                caption=success_text,
                parse_mode="HTML",
                reply_markup=ui.home_only_keyboard(),
            )

        except Exception:

            try:

                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=bot_message,
                    text=success_text,
                    parse_mode="HTML",
                    reply_markup=ui.home_only_keyboard(),
                )

            except Exception:

                await message.answer(
                    success_text,
                    parse_mode="HTML",
                    reply_markup=ui.home_only_keyboard(),
                )

    else:

        await message.answer(
            success_text,
            parse_mode="HTML",
            reply_markup=ui.home_only_keyboard(),
        )

    await state.clear()