from fastapi import APIRouter, Depends, status, HTTPException, status
from app.database import get_db
from sqlalchemy.orm import Session
from app.utils import hash_password
from app import models, schemas, oauth2

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(form: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(form.password)
    new_user = models.User(email=form.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/admin", status_code=status.HTTP_201_CREATED)
def create_admin_user(form: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(form.password)
    new_user = models.User(
        email=form.email, password=hashed_password, role="admin")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/addresses", status_code=status.HTTP_201_CREATED)
def add_address_to_db(data, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="address is empty")
    db.query(models.User).filter(models.User.id == current_user.user_id).update(
        {"address": data}, synchronize_session=False)
    db.commit()
    return {"message": "successful"}


@router.get("/addresses")
def get_address(db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_current_user)):
    return db.query(models.User.address).filter(models.User.id == current_user.user_id).first()
