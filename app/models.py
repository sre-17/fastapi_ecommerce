from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, text, Float, Identity, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=True)
    role = Column(String, nullable=False, server_default=text('user'))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'))


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'))
    discount = relationship("ProductDiscount",  lazy="joined")


class ProductDiscount(Base):
    __tablename__ = "product_discounts"

    product_id = Column(Integer, ForeignKey(
        "products.id", ondelete="CASCADE"),  nullable=False, primary_key=True)
    discounted_price = Column(Integer, nullable=False)


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey(
        "products.id", ondelete="CASCADE"),  nullable=False)
    quantity = Column(Integer, nullable=False, server_default=text('1'))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'))
    fulfilled = Column(Boolean, server_default=text('False'))
    order_id = Column(UUID(as_uuid=True), ForeignKey(
        "orders.transaction_id", ondelete="CASCADE"))


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    transaction_id = Column(
        UUID(as_uuid=True), unique=True, nullable=False)
    price_paid = Column(Integer, nullable=False)
    coupon_code = Column(String, ForeignKey(
        "coupons.code", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'))


class Coupon(Base):
    __tablename__ = "coupons"

    code = Column(String, primary_key=True, nullable=False)
    usage = Column(Integer, nullable=False)
    min_amount = Column(Integer)
    reduction = Column(Integer, nullable=False)
    expiry = Column(TIMESTAMP(timezone=True), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'))


class UserCoupon(Base):
    __tablename__ = "user_coupons"

    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"),  nullable=False, primary_key=True)
    coupon_code = Column(String, ForeignKey(
        "coupons.code", ondelete="CASCADE"),  nullable=False, primary_key=True)
    used = Column(Integer, nullable=False)
