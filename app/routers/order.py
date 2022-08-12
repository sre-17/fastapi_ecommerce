from fastapi import APIRouter, Depends, status, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from uuid import uuid4

router = APIRouter(prefix="/orders", tags=['Orders'])


@router.get("/")
def get_orders(db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    return db.query(models.Order).filter(
        models.Order.user_id == current_user.user_id).all()


@router.post("/")
def create_order(data: schemas.CreateOrder, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    transaction_id = uuid4()
    cart_items = db.query(models.Product,  models.Cart.quantity.label('cart_quantity')).\
        join(models.Cart, models.Product.id == models.Cart.product_id, isouter=True). \
        filter(models.Cart.user_id == current_user.user_id,
               models.Cart.fulfilled == False).all()

    if cart_items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cart is empty")
    if data.code is None:
        new_order = models.Order(status="preparing", transaction_id=transaction_id,
                                 price_paid=data.price_paid, user_id=current_user.user_id)
    else:
        new_order = models.Order(status="preparing", transaction_id=transaction_id,
                                 price_paid=data.price_paid, coupon_code=data.code, user_id=current_user.user_id)
    db.add(new_order)
    db.commit()
    db.query(models.Cart).filter(models.Cart.user_id == current_user.user_id,
                                 models.Cart.fulfilled == False).update({"fulfilled": True, "order_id": transaction_id}, synchronize_session=False)
    db.commit()
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.user_id).all()
    return orders


@router.put("/")
def update_order_status(data: schemas.OrderUpdate, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_admin_user)):
    db.query(models.Order).filter(models.Order.transaction_id == data.transaction_id).update(
        {"status": data.status}, synchronize_session=False)
    return db.query(models.Order).filter(models.Order.transaction_id == data.transaction_id).all()
