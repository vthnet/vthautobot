from aiogram import Router, F
from aiogram.types import CallbackQuery

import ui

from database import get_orders

router = Router()


@router.callback_query(F.data == "orders")
async def orders_history(call: CallbackQuery):

    orders = await get_orders(
        call.from_user.id
    )

    if not orders:

        return await call.answer(
            "No orders yet.",
            show_alert=True
        )

    text = "<b>📜 Recent Orders</b>\n\n"

    for order in orders[:10]:

        status = order["status"].upper()

        text += (
            f"📢 <code>{order['chat_id']}</code>\n"
            f"👀 {order.get('views',0)}\n"
            f"❤️ {order.get('reactions',0)}\n"
            f"📌 {status}\n\n"
        )

    await call.message.edit_text(
        text,
        reply_markup=ui.home_keyboard(),
        parse_mode="HTML",
    )

    await call.answer()