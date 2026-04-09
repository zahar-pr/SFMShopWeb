from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from SFMShopServer.database_v2.models_orm import User, Product, Order, OrderItem


# PRODUCTS
async def get_all_products(session: AsyncSession, limit=10, offset=0):
    total = await session.scalar(select(func.count(Product.id)))
    result = await session.execute(select(Product).order_by(Product.id).limit(limit).offset(offset))
    products = result.scalars().all()
    return total, products


async def get_product_by_id(session: AsyncSession, product_id: int):
    result = await session.get(Product, product_id)
    return result


async def add_new_product(session: AsyncSession, name: str, price, quantity: int):
    product = Product(name=name, price=price, quantity=quantity)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def update_product(session: AsyncSession, product_id: int, name: str, price, quantity: int):
    product = await session.get(Product, product_id)
    if not product:
        return None
    product.name = name
    product.price = price
    product.quantity = quantity
    await session.commit()
    await session.refresh(product)
    return product


async def delete_product(session: AsyncSession, product_id: int):
    product = await session.get(Product, product_id)
    if not product:
        return None
    await session.delete(product)
    await session.commit()
    return product.id


# USERS
async def get_all_users(session: AsyncSession):
    result = await session.execute(select(User).order_by(User.id))
    return result.scalars().all()


async def get_user(session: AsyncSession, user_id: int):
    return await session.get(User, user_id)


async def create_new_user(session, name: str, email: str):
    # сначала проверяем
    result = await session.execute(
        select(User)
        .options(selectinload(User.orders).selectinload(Order.items))
        .where(User.id == user_id)
    )
    if existing_user:
        return existing_user  # пользователь уже есть

    user = User(name=name, email=email)
    session.add(user)
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise
    return user


# ORDERS
async def get_all_orders(session: AsyncSession):
    result = await session.execute(select(Order).order_by(Order.createdat.desc()))
    return result.scalars().all()


async def create_new_order(session: AsyncSession, user_id: int, items: list):
    order = Order(userid=user_id, total=0, createdat=datetime.utcnow())
    session.add(order)
    await session.flush()  # получаем id заказа

    total = 0
    for item in items:
        product = await session.get(Product, item["product_id"])
        if not product:
            raise ValueError(f"Товар {item['product_id']} не найден")
        total += product.price * item["quantity"]
        order_item = OrderItem(orderid=order.id, productid=product.id, quantity=item["quantity"])
        session.add(order_item)

    order.total = total
    await session.commit()
    await session.refresh(order)
    return {"id": order.id, "total": order.total}


async def get_user_order_history(session, user_id: int):
    # загружаем пользователя с заказами и товарами через joinedload
    result = await session.execute(
        select(User)
        .options(
            joinedload(User.orders).joinedload(Order.items).joinedload(OrderItem.product)
        )
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return []

    history = []
    for order in user.orders:
        for item in order.items:
            history.append({
                "user_name": user.name,
                "product_name": item.product.name,
                "price_per_unit": item.product.price,
                "quantity": item.quantity,
                "total_sum": item.product.price * item.quantity
            })
    return history
