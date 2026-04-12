import asyncio
import time
import logging
from typing import Any

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from SFMShopServer.database_v2.models_orm import Order, Product, OrderItem


logger = logging.getLogger(__name__)


async def process_order(order_id: int, session: AsyncSession) -> dict[str, Any] | None:
    try:
        order = await session.get(Order, order_id)

        if not order:
            raise ValueError(f"Order {order_id} not found")

        await asyncio.sleep(0.1)

        order.status = "completed"

        await session.commit()
        await session.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status
        }

    except Exception as e:
        logger.exception(f"Ошибка обработки заказа {order_id}: {e}")
        await session.rollback()
        return None


async def process_orders_async(order_ids: list[int], session: AsyncSession):
    tasks = [process_order(order_id, session) for order_id in order_ids]
    return await asyncio.gather(*tasks, return_exceptions=False)


async def process_orders_sync_demo(order_ids: list[int]):
    results = []
    for order_id in order_ids:
        await asyncio.sleep(0.1)
        results.append({"order_id": order_id, "status": "completed"})
    return results


async def measure_performance(session: AsyncSession):
    order_ids = list(range(1, 101))

    sync_start = time.time()
    await process_orders_sync_demo(order_ids)
    sync_time = time.time() - sync_start

    async_start = time.time()
    await process_orders_async(order_ids, session)
    async_time = time.time() - async_start

    return {
        "sync_time": sync_time,
        "async_time": async_time,
        "speedup": round(sync_time / async_time, 2) if async_time else None
    }


async def fetch_order_details_async(order_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://jsonplaceholder.typicode.com/todos/{order_id}"
            ) as response:
                if response.status != 200:
                    return None
                return await response.json()

    except Exception as e:
        logger.exception(f"HTTP ошибка для заказа {order_id}: {e}")
        return None
