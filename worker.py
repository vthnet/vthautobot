import asyncio
import math
from html import escape
from database import (
    orders,
    get_balance,
    change_credits,
    add_history,
    get_channel,
    update_channel,
    get_settings,
    calculate_order_credits,
)

from panel import add_order
from logger import log

async def worker(bot):

    while True:

        order = await orders.find_one(
            {"status": "pending"}
        )

        if not order:
            await asyncio.sleep(3)
            continue

        settings = await get_settings()

        channel = await get_channel(order["chat_id"])
        if not channel:

          await orders.update_one(
        {"_id": order["_id"]},
        {
            "$set": {
                "status": "failed",
                "error": "Channel not found"
            }
        }
    )
          await log(
             bot,
             "Order Failed",
             f"""
👤 <code>{order['owner']}</code>

Reason:
Channel not found.
""",
    "❌",
)

          try:
             await bot.send_message(
        order["owner"],
        """
❌ <b>Boost Failed</b>

Channel not found.

Please add the channel again.
""",
        parse_mode="HTML",
    )
          except Exception:
            pass

          await asyncio.sleep(1)
          continue

        view_cost, reaction_cost, required = calculate_order_credits(
            order.get("views", 0),
            order.get("reactions", 0),
            settings,
        )
        balance = await get_balance(order["owner"])

        if balance < required:

            await orders.update_one(
               {"_id": order["_id"]},
               {
                  "$set": {
                      "status": "paused",
                     "error": "Insufficient credits"
                    }
              }
         )

            try:
                await bot.send_message(
                   order["owner"],
                   f"""
⏸ <b>Auto Boost Paused</b>

📢 <b>{escape(channel.get('title') or 'Unknown Channel')}</b>

❌ Insufficient credits.

💰 Current Balance
<b>{balance}</b>

💸 Required
<b>{required}</b>

💳 Recharge your wallet.

✅ Your order will resume automatically after recharge.
""",
            parse_mode="HTML",
        )

            except Exception:
              pass

            await log(
               bot,
        "Order Paused",
        f"""
👤 <code>{order['owner']}</code>

📢 {escape(channel.get('title') or 'Unknown Channel')}

Reason:
Insufficient Credits

Balance: {balance}

Required: {required}
""",
        "⏸"
    )

            await asyncio.sleep(1)
            continue

        if not channel.get("username"):

            await orders.update_one(
                {"_id": order["_id"]},
                {
                    "$set": {
                        "status": "failed",
                        "error": "Private channel"
                    }
                }
            )
            try:
              await bot.send_message(
               order["owner"],
    """
❌ <b>Boost Failed</b>

Your channel is private.

Please make it public and try again.
""",
        parse_mode="HTML",
    )
            except Exception:
                pass

            await log(
               bot,
               "Order Failed",
               f"""
            👤 <code>{order['owner']}</code>

            📢 {escape(channel.get('title') or 'Unknown Channel')}

            Reason:
            Private channel.
            """,
               "❌",
)

            await asyncio.sleep(1)
            continue

        post_link = (
            f"https://t.me/"
            f"{channel['username']}/"
            f"{order['message_id']}"
        )

        view_order = None
        reaction_order = None

        # Views
        if order.get("views", 0) > 0:

            for _ in range(3):

                try:

                    result = await add_order(
                        settings["view_service"],
                        post_link,
                        order["views"],
                    )
                    if result.get("error"):
                        print(result)
                    if result.get("order"):
                        view_order = result["order"]
                        break

                except Exception as e:
                    print(f"View Order Error: {e}")
                    await asyncio.sleep(2)

        # Reactions
        if order.get("reactions", 0) > 0:

            for _ in range(3):

                try:

                    result = await add_order(
                        settings["reaction_service"],
                        post_link,
                        order["reactions"],
                    )
                    if result.get("error"):
                       print(result)
                    if result.get("order"):
                        reaction_order = result["order"]
                        break

                except Exception as e:
                   print(f"Reaction Order Error: {e}")
                   await asyncio.sleep(2)

        if (
            (order.get("views", 0) == 0 or view_order)
            and
            (order.get("reactions", 0) == 0 or reaction_order)
        ):

            await change_credits(
                order["owner"],
                -required
            )
            await add_history(
                order["owner"],
                -required,
                (
                    f"🚀 Auto Boost\n"
                    f"👀 {order.get('views', 0)} Views\n"
                    f"❤️ {order.get('reactions', 0)} Reactions"
                ),
                "boost",
            )
            await update_channel(
                order["chat_id"],
                {
                   "posts_boosted": channel.get("posts_boosted", 0) + 1,
                   "views_sent": channel.get("views_sent", 0) + order.get("views", 0),
                   "reactions_sent": channel.get("reactions_sent", 0) + order.get("reactions", 0),
                   "credits_used": channel.get("credits_used", 0) + required,
                }
            ) 
    
            await orders.update_one(
                {"_id": order["_id"]},
                {
                    "$set": {
                        "status": "completed",
                        "view_order": view_order,
                        "reaction_order": reaction_order,
                        "credits_used": required,
                    }
                }
            )
            balance = await get_balance(
               order["owner"]
           )

            try:

              await bot.send_message(
                  order["owner"],
                  f"""
🚀 <b>Auto Boost Started</b>
<blockquote>--------------------------------------------------
📢 <b>Channel</b> :<b>{escape(channel.get('title') or 'Unknown Channel')}</b>
👀 <b>Views</b> :<b>{order['views']}</b>
❤️ <b>Reactions</b> :<b>{order['reactions']}</b>
💸 <b>Credits Used</b> :<b>{required}</b>
💰 <b>Credits Left</b> :<b>{balance}</b>
🆔 <b>View Order</b> :<code>{view_order or "N/A"}</code>
🆔 <b>Reaction Order</b> :<code>{reaction_order or "N/A"}</code>
--------------------------------------------------</blockquote>
✅ Your boost order has been placed successfully.
""",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

            except Exception as e:
               print(f"User notification error: {e}")
 
            await log(
               bot,
               "New Auto Boost Order",
               f"""
<blockquote>👤 <b>User</b> :<code>{order['owner']}</code>

📢 {escape(channel.get('title') or 'Unknown Channel')}

🔗 <b>Post</b> :{post_link}

👀 <b>Views</b> :{order.get('views', 0)}

❤️ <b>Reactions</b> :{order.get('reactions', 0)}

💸 <b>Credits Used</b> :{required}

💰 <b>Credits Left</b> :{balance}

🆔 <b>View Order</b> :<code>{view_order or 'N/A'}</code>

🆔 <b>Reaction Order</b> :<code>{reaction_order or 'N/A'}</code></blockquote>
""",
    "🚀"
)
            print(
                f"✅ Order Completed | {order['_id']}"
            )

        else:

           await orders.update_one(
              {"_id": order["_id"]},
              {
                  "$set": {
                     "status": "failed",
                     "error": "Panel rejected order"
                 }
              }
          )

           try:
                await bot.send_message(
            order["owner"],
            f"""
❌ <b>Auto Boost Failed</b>
--------------------------------------------------
📢 <b>Channel</b> :{escape(channel.get('title') or 'Unknown Channel')}

🔗 <b>Post</b> :{post_link}
--------------------------------------------------
The provider rejected your order.
No credits were deducted.
Please try again later.
""",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
           except Exception:
             pass

           await log(
        bot,
        "Auto Boost Failed",
        f"""
👤 <code>{order['owner']}</code>
📢 {escape(channel.get('title') or 'Unknown Channel')}
🔗 {post_link}
Reason: Panel rejected order.
""",
        "❌",
    )

           print(f"❌ Order Failed | {order['_id']}")
        await asyncio.sleep(1)