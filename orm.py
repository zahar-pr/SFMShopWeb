from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Связь с заказами
    orders = relationship("Order", back_populates="user")


class Product(Base):
    """Модель товара"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class Order(Base):
    """Модель заказа"""
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total = Column(Decimal(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Связь с пользователем
    user = relationship("User", back_populates="orders")