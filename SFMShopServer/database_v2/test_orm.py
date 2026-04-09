import asyncio
from SFMShopServer.database_v2.connection_orm import AsyncSessionLocal
from queries_orm import create_new_user, add_new_product, create_new_order, get_user_order_history

async def test():
    async with AsyncSessionLocal() as session:
        user = await create_new_user(session, "Alice", "alice@example.com")
        print(user.id, user.name)

        product = await add_new_product(session, "Laptop", 1000.0, 5)
        print(product.id, product.name)

        order = await create_new_order(session, user.id, [{"product_id": product.id, "quantity": 2}])
        print(order)

        history = await get_user_order_history(session, user.id)
        print(history)


asyncio.run(test())
