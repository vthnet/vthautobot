from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI
from datetime import datetime
import math
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

client = AsyncIOMotorClient(MONGO_URI)

db = client.vth_auto_boost

users = db.users
channels = db.channels
orders = db.orders
settings = db.settings
stats = db.stats
referrals = db.referrals
history = db.history
payments = db.payments
bot_settings = db.bot_settings

async def get_user(user_id: int):
    return await users.find_one({"_id": user_id})


async def create_user(data: dict):
    await users.insert_one(data)


async def update_user(user_id: int, data: dict):
    await users.update_one(
        {"_id": user_id},
        {"$set": data}
    )

async def add_credits(user_id: int, amount: int):
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"credits": amount}}
    )

async def change_credits(user_id: int, amount: int):
    return await users.update_one(
        {"_id": user_id},
        {"$inc": {"credits": amount}}
    )


async def get_balance(user_id: int):
    user = await users.find_one(
        {"_id": user_id},
        {"credits": 1}
    )
    return user.get("credits", 0) if user else 0

async def add_history(
    user_id: int,
    amount: int,
    reason: str,
    transaction_type: str = "other",
):

    await history.insert_one(
        {
            "user_id": user_id,
            "amount": amount,
            "reason": reason,
            "type": transaction_type,
            "time": datetime.utcnow(),
        }
    )

async def get_channel(chat_id: int):
    return await channels.find_one({"_id": chat_id})


async def get_history(user_id: int, limit: int = 10):
    return await history.find(
        {"user_id": user_id}
    ).sort("time", -1).to_list(limit)


async def get_channels(user_id: int):
    return await channels.find(
        {"owner": user_id}
    ).to_list(None)


async def add_channel(data: dict):
    await channels.insert_one(data)


async def update_channel(chat_id: int, data: dict):
    await channels.update_one(
        {"_id": chat_id},
        {"$set": data}
    )


async def delete_channel(chat_id: int):
    await channels.delete_one(
        {"_id": chat_id}
    )

async def create_payment(data: dict):
    result = await payments.insert_one(data)
    return result.inserted_id


async def get_payment(payment_id: str):
    return await payments.find_one(
        {"_id": ObjectId(payment_id)}
    )


async def update_payment(payment_id: str, data: dict):
    await payments.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": data}
    )

async def ensure_order_indexes():
    """
    Create a sparse unique index for logical channel-post deduplication.
    Existing orders without post_key are unaffected.
    """
    await orders.create_index(
        [("post_key", 1)],
        unique=True,
        sparse=True,
        name="unique_post_key",
    )


def calculate_order_credits(views: int, reactions: int, settings: dict) -> tuple[int, int, int]:
    """
    Return (view_credits, reaction_credits, total_credits) using the
    exact same ceil-based conversion used by the worker.
    """
    views_per_credit = max(1, int(settings.get("views_per_credit", 50)))
    reactions_per_credit = max(1, int(settings.get("reactions_per_credit", 5)))

    view_credits = (
        math.ceil(int(views or 0) / views_per_credit)
        if views
        else 0
    )
    reaction_credits = (
        math.ceil(int(reactions or 0) / reactions_per_credit)
        if reactions
        else 0
    )

    return view_credits, reaction_credits, view_credits + reaction_credits


async def create_order(data: dict):
    try:
        await orders.insert_one(data)
        return True
    except DuplicateKeyError:
        # A channel post with the same logical post_key was already queued.
        return False


settings = db.settings

BOT_SETTINGS = {
    "_id": "bot",

    "start_text": """
👋 Welcome to VTH AUTO BOT

Use the menu below.
""",

    "start_photo": None,
}

DEFAULT_SETTINGS = {

    "_id": "settings",

    "credits_per_rupee": 50,

    "views_per_credit": 50,

    "reactions_per_credit": 5,

    "referral_reward": 50,

    "view_service": 344,

    "reaction_service": 3960,

    "force_join": "@vthnet",

    "min_views": 20,

    "max_views": 9000,

    "min_reactions": 20,

    "max_reactions": 5000,
}


async def get_settings():
    data = await settings.find_one(
        {"_id": "settings"}
    )
    if not data:
        await settings.insert_one(
            DEFAULT_SETTINGS.copy()
        )
        data = await settings.find_one(
            {"_id": "settings"}
        )
    updated = False
    for key, value in DEFAULT_SETTINGS.items():
         if key not in data:
            data[key] = value
            updated = True
    if updated:
        await settings.update_one(
          {"_id": "settings"},
          {"$set": data}
    )
    return data

async def update_settings(data: dict):
    await settings.update_one(
        {"_id": "settings"},
        {"$set": data},
        upsert=True
    )

async def resume_orders(user_id: int):
    result = await orders.update_many(
        {
            "owner": user_id,
            "status": "paused"
        },
        {
            "$set": {
                "status": "pending",
                "error": None,
            }
        }
    )

    return result.modified_count

async def get_orders(user_id: int, limit: int = 20):
    return await orders.find(
        {"owner": user_id}
    ).sort("_id", -1).to_list(limit)


async def get_bot_settings():

    data = await bot_settings.find_one(
        {"_id": "bot"}
    )

    if not data:

        await bot_settings.insert_one(
            BOT_SETTINGS.copy()
        )

        data = await bot_settings.find_one(
            {"_id": "bot"}
        )

    return data


async def update_bot_settings(data):

    await bot_settings.update_one(
        {"_id": "bot"},
        {"$set": data},
        upsert=True,
    )