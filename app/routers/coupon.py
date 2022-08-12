from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, oauth2, schemas
router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_coupon(data: schemas.CouponCreate, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_admin_user)):
    # 2020-05-12T23:50:21.817Z  js date.toISOString()
    expiry = datetime.strptime(data.expiry, '%Y-%m-%dT%H:%M:%S')
    new_coupon = models.Coupon(
        code=data.code, expiry=expiry, coupon_type=data.coupon_type)
    db.add(new_coupon)
    db.commit()
    db.refresh(new_coupon)
    return new_coupon


@router.put("/{coupon_code}")
def update_coupon(coupon_code: str, data: schemas.CouponUpdate, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_admin_user)):
    query = db.query(models.Coupon).filter(models.Column.code == coupon_code)
    if query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid coupon code")
    query.update(**data.dict(), synchronize_session=False)
    return query.first()


@router.delete("/{coupon_code}")
def delete_coupon(coupon_code: str, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_admin_user)):
    query = db.query(models.Coupon).filter(models.Column.code == coupon_code)
    if query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid coupon code")
    query.delete(synchronize_session=False)
    Response(status_code=status.HTTP_204_NO_CONTENT)
