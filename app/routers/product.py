from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.database import get_db
from sqlalchemy.orm import Session
from app import models, oauth2, schemas
router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Product)
def create_item(item: schemas.ProductCreate, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_admin_user)):
    product = models.Product(**item.dict())
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.get("/", response_model=list[schemas.ProductShort])
def get_products(db: Session = Depends(get_db), skip: int = 0, limit: int = 10, search: str | None = None):
    if search is None:
        return db.query(models.Product).all()
    else:
        return db.query(models.Product).filter(models.Product.name.contains(search)).limit(limit).offset(skip).all()


@router.get("/{item_id}", response_model=schemas.Product)
def get_product_details(item_id: int, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.id == item_id).first()


@router.put("/{item_id}", response_model=schemas.Product)
def update_product(item_id: int, item: schemas.ProductCreate, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_admin_user)):
    query = db.query(models.Product).filter(models.Product.id == item_id)

    if query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {item_id} not found")

    query.update(item.dict(), synchronize_session=False)
    db.commit()
    return query.first()


@router.delete("/{item_id}")
def delete_product(item_id: int, db: Session = Depends(get_db), current_user: schemas.JwtUser = Depends(oauth2.get_admin_user)):
    query = db.query(models.Product).filter(models.Product.id == item_id)
    to_delete = query.first()
    if to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {item_id} not found")
    query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
