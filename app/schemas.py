from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(BaseModel):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class JwtUser(BaseModel):
    user_id: int
    role: str


class Discount(BaseModel):
    discounted_price: int | None

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name: str
    description: str
    price: float


class ProductCreate(ProductBase):
    quantity: int


class Product(ProductBase):
    id: str
    created_at: datetime
    quantity: int
    discount: list[Discount]

    class Config:
        orm_mode = True


class ProductShort(ProductBase):
    id: str
    quantity: int
    discount: list[Discount]

    class Config:
        orm_mode = True


class CartAdd(BaseModel):
    product_id: int
    quantity: int | None = 1


class CartUpdate(BaseModel):
    product_id: int
    quantity: int


class CartProducts(BaseModel):
    Product: Product
    cart_quantity: int


class Cart(BaseModel):
    products: list[CartProducts]
    total_items: int
    total_price: int

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    user_id: int
    product_id: int


class OrderBase(OrderCreate):
    quantity: int
    price: int
    transaction_id: str


class OrderUpdate(BaseModel):
    status: Literal['preparing', 'on the way', 'delivered']
    transaction_id: str


class CouponBase(BaseModel):
    usage: str
    expiry: datetime


class CouponCreate(CouponBase):
    code: str


class CouponUpdate(BaseModel):
    expiry: datetime


class CreateOrder(BaseModel):
    price_paid: int
    code: str | None = None
