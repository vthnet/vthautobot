import httpx

from config import (
    PANEL_URL,
    PANEL_KEY,
)


async def api(data: dict):

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        r = await client.post(
            PANEL_URL,
            data={
                "key": PANEL_KEY,
                **data
            }
        )

        r.raise_for_status()

        return r.json()


async def services():

    return await api(
        {
            "action": "services"
        }
    )


async def add_order(
    service: int,
    link: str,
    quantity: int,
):

    return await api(
        {
            "action": "add",
            "service": service,
            "link": link,
            "quantity": quantity,
        }
    )


async def status(order_id):

    return await api(
        {
            "action": "status",
            "order": order_id,
        }
    )


async def multi_status(ids):

    return await api(
        {
            "action": "status",
            "orders": ",".join(
                map(str, ids)
            ),
        }
    )