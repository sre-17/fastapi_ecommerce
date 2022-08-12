from fastapi import APIRouter, Depends, status, HTTPException, Response
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from datetime import datetime, timezone
router = APIRouter(prefix="/carts", tags=["Shopping cart"])


def get_product_details(db, product_id):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_total_price(db, current_user):
    cart_items = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.user_id, models.Cart.fulfilled == False).all()
    total_price = 0
    for cart_item in cart_items:
        product = db.query(models.Product).filter(
            models.Product.id == cart_item.product_id).first()
        if len(product.discount) > 0:
            total_price += product.discount[0].discounted_price * \
                cart_item.quantity
        else:
            total_price += product.price * cart_item.quantity
    return total_price


@router.get("/")
def get_cart_items(db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    cart_items = db.query(models.Product,  models.Cart.quantity.label('cart_quantity'), models.Cart.id).\
        join(models.Cart, models.Product.id == models.Cart.product_id, isouter=True). \
        filter(models.Cart.user_id == current_user.user_id,
               models.Cart.fulfilled == False).all()
    total_price = get_total_price(db, current_user)
    response = schemas.Cart(products=cart_items, total_items=len(
        cart_items), total_price=total_price)

    return response


@router.post("/apply_coupon")
def check_coupon_and_apply(data, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):

    coupon = db.query(models.Coupon).filter(
        models.Coupon.code == data).first()
    if coupon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid coupon code")
    user_coupon = db.query(models.UserCoupon).filter(models.UserCoupon.coupon_code ==
                                                     data, models.UserCoupon.user_id == current_user.user_id).first()
    if coupon.expiry > datetime.now(timezone.utc):
        total_price = get_total_price(db, current_user)
        if(user_coupon is None or user_coupon.used < coupon.usage):
            if total_price >= coupon.min_amount:
                total_price -= total_price * (coupon.reduction / 100)
                return {"message": "coupon applied", "total_price": total_price}
            else:
                return {"message": f"purchase value should be greater than {coupon.min_amount}"}
        else:
            return {"message": "coupon is not available for this user"}
    else:
        return {"message": "coupon expired"}


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_cart(data: schemas.CartAdd, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    product = get_product_details(db, data.product_id)
    # start checks for unauthorized modification and bad data entry
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id: {data.product_id} not found")

    query = db.query(models.Cart).filter(
        models.Cart.product_id == data.product_id, models.Cart.user_id == current_user.user_id, models.Cart.fulfilled == False)
    if query.first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Product already in cart")

    if data.quantity > product.quantity or data.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Requested quantity not available")
    # end checks
    new_cart_item = models.Cart(
        product_id=data.product_id, user_id=current_user.user_id, quantity=data.quantity)
    db.add(new_cart_item)
    db.commit()
    return {"message": "successful"}


@router.put("/edit")
def edit_item_quantity(data: schemas.CartUpdate, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    query = db.query(models.Cart).filter(
        models.Cart.product_id == data.product_id, models.Cart.user_id == current_user.user_id,
        models.Cart.fulfilled == False)
    cart_details = query.first()
    # start checks for unauthorized modification and bad data entry
    if cart_details is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")

    product = get_product_details(db, cart_details.product_id)
    if data.quantity > product.quantity or data.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Requested quantity not available")
    # end checks
    query.update({"quantity": data.quantity}, synchronize_session=False)
    db.commit()
    return {"message": "successful"}


@router.delete("/remove")
def delete_cart_item(product_id: int, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    query = db.query(models.Cart).filter(
        models.Cart.product_id == product_id, models.Cart.user_id == current_user.user_id,
        models.Cart.fulfilled == False)
    if query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")

    query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
