from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import FORCE_JOIN_CHANNEL, OWNER_ID


def home_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="📢 My Channels",
        callback_data="channels"
    )
    kb.button(
        text="💳 Wallet",
        callback_data="wallet"
    )
    kb.button(
        text="👥 Refer & Earn",
        callback_data="refer"
    )
    kb.button(
        text="📊 Statistics",
        callback_data="stats"
    )
    kb.button(
        text="📖 How To Use",
        callback_data="guide"
    )
    kb.button(
        text="🛟 Support",
        callback_data="support"
    )
    kb.adjust(2, 2, 2)
    return kb.as_markup()


def force_join_keyboard():
    kb = InlineKeyboardBuilder()

    channel = FORCE_JOIN_CHANNEL.replace("@", "")

    kb.button(
        text="📢 Join Channel",
        url=f"https://t.me/{channel}"
    )

    kb.button(
        text="✅ I've Joined",
        callback_data="verify_join"
    )

    kb.adjust(1)

    return kb.as_markup()


def wallet_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="💰 Buy Credits",
        callback_data="buy"
    )

    kb.button(
        text="🔙 Back",
        callback_data="home"
    )

    kb.adjust(1, 1)

    return kb.as_markup()


def buy_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(text="₹100", callback_data="buy_100")
    kb.button(text="₹250", callback_data="buy_250")

    kb.button(text="₹500", callback_data="buy_500")
    kb.button(text="₹1000", callback_data="buy_1000")

    kb.button(
        text="🔙 Back",
        callback_data="wallet"
    )

    kb.adjust(2, 2, 1)

    return kb.as_markup()


def cancel_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="❌ Cancel",
        callback_data="home"
    )

    return kb.as_markup()


def admin_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="📊 Statistics",
        callback_data="admin_stats"
    )
    kb.button(
        text="💳 Payments",
        callback_data="admin_payments"
    )
    kb.button(
        text="👥 Users",
        callback_data="admin_users"
    )
    kb.button(
        text="📢 Channels",
        callback_data="admin_channels"
    )
    kb.button(
        text="📢 Broadcast",
        callback_data="broadcast"
    )
    kb.button(
        text="⚙ Settings",
        callback_data="admin_settings"
    )
    kb.button(
        text="🔙 Home",
        callback_data="home"
    )
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()


def channels_keyboard(channels):
    kb = InlineKeyboardBuilder()

    if channels:
        for channel in channels:
            title = (
                channel.get("title")
                or channel.get("username")
                or str(channel["_id"])
            )
            kb.button(
                text=f"📢 {title}",
                callback_data=f"channel_{channel['_id']}"
            )
    kb.button(
        text="➕ Add Channel",
        callback_data="add_channel"
    )
    kb.button(
        text="🔙 Back",
        callback_data="home"
    )
    kb.adjust(1)
    return kb.as_markup()


def channel_keyboard(chat_id: int):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🟢 Auto ON/OFF",
        callback_data=f"toggle_{chat_id}"
    )

    kb.button(
        text="👀 Auto Views",
        callback_data=f"views_{chat_id}"
    )

    kb.button(
        text="❤️ Auto Reactions",
        callback_data=f"reactions_{chat_id}"
    )

    kb.button(
        text="🗑 Delete Channel",
        callback_data=f"delete_{chat_id}"
    )

    kb.button(
        text="🔙 Back",
        callback_data="channels"
    )

    kb.adjust(1, 2, 1, 1)

    return kb.as_markup()


def referral_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🔙 Back",
        callback_data="home"
    )
    return kb.as_markup()

def guide_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📺 Open Guide",
        url="https://t.me/Vthbotguide/6"
    )
    kb.button(
        text="🏠 Home",
        callback_data="home"
    )
    kb.adjust(1)
    return kb.as_markup()


def support_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="👤 Contact Support",
        url="https://t.me/vthnetsupport"
    )
    kb.button(
        text="🏠 Home",
        callback_data="home"
    )
    kb.adjust(1)
    return kb.as_markup()

def payment_keyboard(payment_id):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅ Approve",
        callback_data=f"approve_{payment_id}"
    )
    kb.button(
        text="❌ Reject",
        callback_data=f"reject_{payment_id}"
    )
    kb.button(
        text="🔙 Admin",
        callback_data="admin"
    )
    kb.adjust(2,1)
    return kb.as_markup()


def settings_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="👀 Views / Credit",
        callback_data="set_views_per_credit"
    )
    kb.button(
        text="❤️ Reactions / Credit",
        callback_data="set_reactions_per_credit"
    )
    kb.button(
        text="🎁 Referral Reward",
        callback_data="set_referral"
    )
    kb.button(
        text="💰 Credits / ₹1",
        callback_data="set_rupee"
    )
    kb.button(
        text="👀 Min Views",
        callback_data="set_min_views"
    )
    kb.button(
        text="👀 Max Views",
        callback_data="set_max_views"
    )
    kb.button(
        text="❤️ Min Reactions",
        callback_data="set_min_reactions"
    )
    kb.button(
        text="❤️ Max Reactions",
        callback_data="set_max_reactions"
    )
    kb.button(
        text="📢 Force Join",
        callback_data="set_force_join"
    )
    kb.button(
        text="🆔 View Service",
        callback_data="set_view_service"
    )
    kb.button(
        text="🆔 Reaction Service",
        callback_data="set_reaction_service"
    )
    kb.button(
        text="🔙 Admin",
        callback_data="admin"
    )
    kb.adjust(
        2,
        2,
        2,
        2,
        1,
        2,
        1
    )
    return kb.as_markup()


def payment_confirm_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅ I've Paid",
        callback_data="payment_done"
    )
    kb.button(
        text="❌ Cancel",
        callback_data="wallet"
    )
    kb.adjust(2)
    return kb.as_markup()

def home_only_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🏠 Home",
        callback_data="home"
    )

    return kb.as_markup()

def back_home_keyboard(chat_id):
    kb = InlineKeyboardBuilder()

    kb.button(
        text="⬅ Back",
        callback_data=f"channel_{chat_id}",
    )

    kb.button(
        text="🏠 Home",
        callback_data="home",
    )

    kb.adjust(2)

    return kb.as_markup()


def back_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="🔙 Back",
        callback_data="home"
    )

    return kb.as_markup()