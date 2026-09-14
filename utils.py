from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto

from config import FORCE_JOIN_CHANNEL, OWNER_ID


async def joined(bot, user_id: int) -> bool:

    if user_id == OWNER_ID:
        return True

    try:
        member = await bot.get_chat_member(
            FORCE_JOIN_CHANNEL,
            user_id,
        )
        return member.status not in (
            "left",
            "kicked",
        )

    except TelegramBadRequest:
        return False


async def edit_or_send(
    call,
    text: str,
    keyboard=None,
):
    """
    Smart editor.

    • If current message is a photo → edits caption.
    • If current message is text → edits text.
    • If editing fails → sends a new message instead.
    """

    try:

        # Current message is PHOTO
        if call.message.photo:

            await call.message.edit_caption(
                caption=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

        # Current message is TEXT
        else:

            await call.message.edit_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    except TelegramBadRequest:

        try:

            if call.message.photo:

                await call.message.answer_photo(
                    photo=call.message.photo[-1].file_id,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

            else:

                await call.message.answer(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

        except Exception:
            pass