from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import FORCE_JOIN_CHANNEL, OWNER_ID


def home_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="My Channels",
        callback_data="channels",
        style="success",icon_custom_emoji_id="4992560350982309130"
    )
    kb.button(
        text="Wallet",
        callback_data="wallet",
        style="primary", icon_custom_emoji_id="5256186332669035163"
    )
    kb.button(
        text="Refer & Earn",
        callback_data="refer",
        style="primary", icon_custom_emoji_id="5226431245918942763"
    )
    kb.button(
        text="Statistics",
        callback_data="stats",
        style="primary", icon_custom_emoji_id="5190806721286657692"
    )
    kb.button(
        text="How To Use",
        callback_data="guide",
        style="success", icon_custom_emoji_id="5377537549831005036"
    )
    kb.button(
        text="Support",
        callback_data="support",
        style="success", icon_custom_emoji_id="5238025132177369293"
    )
    kb.adjust(1, 2, 1, 2)
    return kb.as_markup()


def force_join_keyboard():
    kb = InlineKeyboardBuilder()

    channel = FORCE_JOIN_CHANNEL.replace("@", "")

    kb.button(
        text="Join Channel",
        url=f"https://t.me/{channel}",icon_custom_emoji_id="4992560350982309130", style="primary"
    )

    kb.button(
        text="I've Joined",
        callback_data="verify_join",icon_custom_emoji_id="5980930633298350051", style="success"
    )

    kb.adjust(1)

    return kb.as_markup()


def wallet_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="Buy Credits",
        callback_data="buy",icon_custom_emoji_id="5382164415019768638"
    )

    kb.button(
        text="Back",
        callback_data="home",icon_custom_emoji_id="5409284148491726576", style="danger"
    )

    kb.adjust(1, 1)

    return kb.as_markup()


def buy_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(text="₹100", callback_data="buy_100",style="primary")
    kb.button(text="₹250", callback_data="buy_250",style="primary")

    kb.button(text="₹500", callback_data="buy_500",style="primary")
    kb.button(text="₹1000", callback_data="buy_1000",style="primary")

    kb.button(
        text="Back",
        callback_data="wallet",icon_custom_emoji_id="5409284148491726576",style="danger"
    )

    kb.adjust(2, 2, 1)

    return kb.as_markup()


def cancel_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="Cancel",
        callback_data="home",icon_custom_emoji_id="5974083768233760323"
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
        callback_data="admin_payments",
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
                text=f" {title}",
                callback_data=f"channel_{channel['_id']}",icon_custom_emoji_id="4992560350982309130"
            )
    kb.button(
        text="Add Channel",
        callback_data="add_channel",icon_custom_emoji_id="5287354223141342798"
    )
    kb.button(
        text="Back",
        callback_data="home",icon_custom_emoji_id="5409284148491726576",style="danger"
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
        text="Auto Views",
        callback_data=f"views_{chat_id}",icon_custom_emoji_id="5039623284056917259"
    )

    kb.button(
        text="Auto Reactions",
        callback_data=f"reactions_{chat_id}",icon_custom_emoji_id="5902223360439357399"
    )

    kb.button(
        text="Delete Channel",
        callback_data=f"delete_{chat_id}",icon_custom_emoji_id="5408832111773757273"
    )

    kb.button(
        text="Back",
        callback_data="channels",icon_custom_emoji_id="5409284148491726576",style="danger"
    )

    kb.adjust(1, 2, 1, 1)

    return kb.as_markup()


def referral_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Back",
        callback_data="home",icon_custom_emoji_id="5409284148491726576",style="danger"
    )
    return kb.as_markup()

def guide_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="Open Guide",
        url="https://t.me/Vthbotguide/6",icon_custom_emoji_id="5355012477883004708"
    )
    kb.button(
        text="Home",
        callback_data="home",icon_custom_emoji_id="5395831812704452001"
    )
    kb.adjust(1)
    return kb.as_markup()


def support_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text=" Contact Support",
        url="https://t.me/vthnetsupport",icon_custom_emoji_id="5983494174723279869"
    )
    kb.button(
        text="Home",
        callback_data="home",icon_custom_emoji_id="5395831812704452001"
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
        text="I've Paid",
        callback_data="payment_done",icon_custom_emoji_id="5980930633298350051",style="success"
    )
    kb.button(
        text="Cancel",
        callback_data="wallet",icon_custom_emoji_id="5974083768233760323",style="danger"
    )
    kb.adjust(2)
    return kb.as_markup()

def home_only_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Home",
        callback_data="home",icon_custom_emoji_id="5395831812704452001"
    )

    return kb.as_markup()

def back_home_keyboard(chat_id):
    kb = InlineKeyboardBuilder()

    kb.button(
        text="Back",
        callback_data=f"channel_{chat_id}",icon_custom_emoji_id="5409284148491726576",style="danger"
    )

    kb.button(
        text="Home",
        callback_data="home",icon_custom_emoji_id="5395831812704452001"
    )

    kb.adjust(2)

    return kb.as_markup()


def back_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="Back",
        callback_data="home",icon_custom_emoji_id="5409284148491726576",style="danger"
    )

    return kb.as_markup()