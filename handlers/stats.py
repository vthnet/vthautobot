from aiogram import Router, F
from aiogram.types import CallbackQuery

import ui
from utils import edit_or_send
from database import (
    get_user,
    get_channels,
    get_settings,
    orders,
    payments,
    referrals,
)

router = Router()


@router.callback_query(F.data == "stats")
async def statistics(call: CallbackQuery):

    user = await get_user(call.from_user.id)

    if not user:
        return await call.answer(
            "User not found.",
            show_alert=True
        )

    user_channels = await get_channels(
        call.from_user.id
    )

    total_orders = await orders.count_documents(
        {
            "owner": call.from_user.id
        }
    )

    completed_orders = await orders.count_documents(
        {
            "owner": call.from_user.id,
            "status": "completed"
        }
    )

    pending_orders = await orders.count_documents(
        {
            "owner": call.from_user.id,
            "status": "pending"
        }
    )

    paused_orders = await orders.count_documents(
        {
            "owner": call.from_user.id,
            "status": "paused"
        }
    )

    failed_orders = await orders.count_documents(
        {
            "owner": call.from_user.id,
            "status": "failed"
        }
    )

    pipeline = [
        {
            "$match": {
                "owner": call.from_user.id
            }
        },
        {
            "$group": {
                "_id": None,
                "views": {
                    "$sum": "$views"
                },
                "reactions": {
                    "$sum": "$reactions"
                },
                "credits_used": {
                    "$sum": {
                        "$ifNull": [
                            "$credits_used",
                            0
                        ]
                    }
                }
            }
        }
    ]

    totals = await orders.aggregate(
        pipeline
    ).to_list(1)

    if totals:

        total_views = totals[0]["views"]
        total_reactions = totals[0]["reactions"]
        credits_used = totals[0]["credits_used"]

    else:

        total_views = 0
        total_reactions = 0
        credits_used = 0

    payment_pipeline = [
        {
            "$match": {
                "user_id": call.from_user.id,
                "status": "approved"
            }
        },
        {
            "$group": {
                "_id": None,
                "credits": {
                    "$sum": "$credits"
                }
            }
        }
    ]

    payment = await payments.aggregate(
        payment_pipeline
    ).to_list(1)

    purchased = (
        payment[0]["credits"]
        if payment
        else 0
    )

    referral_count = await referrals.count_documents(
        {
            "referrer": call.from_user.id
        }
    )

    settings = await get_settings()

    referral_rewards = (
       referral_count *
       settings["referral_reward"]
   )
    joined = user.get(
        "created_at"
    )

    joined = (
        joined.strftime("%d %b %Y")
        if joined
        else "Unknown"
    )

    await edit_or_send(
    call,
    f"""
📊 <b>Your Statistics</b>
-------------------------------------------------------
<blockquote>💰 Wallet :<b>{user.get('credits',0):,}</b> Credits
📢 Channels :<b>{len(user_channels)}</b>
🚀 Orders :<b>{total_orders}</b>

-------------------------------------------------------
✅ Completed :<b>{completed_orders}</b>
⏳ Pending :<b>{pending_orders}</b>
⏸ Paused :<b>{paused_orders}</b>
❌ Failed :<b>{failed_orders}</b>

-------------------------------------------------------
👀 Views Ordered :<b>{total_views:,}</b>
❤️ Reactions Ordered :<b>{total_reactions:,}</b>

-------------------------------------------------------
💳 Credits Purchased :<b>{purchased:,}</b>
💸 Credits Used :<b>{credits_used:,}</b>
👥 Referrals :<b>{referral_count}</b>
🎁 Referral Rewards :<b>{referral_rewards:,}</b>
</blockquote>
-------------------------------------------------------
📅 Joined :<b>{joined}</b>
""",
    ui.back_keyboard(),
)

    await call.answer()