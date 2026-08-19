from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.products import Product
from app.schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from sqlalchemy import select
import app.crud.product as product_crud

from sqlalchemy.orm import joinedload
from app.models.products import Product

from typing import Optional
from fastapi import Query
from app.security import get_current_admin
from app.models.user import User
import os
import shutil
import uuid

from fastapi import UploadFile, File
from pathlib import Path
from fastapi import status

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

""" products = []

@router.get(
    "/",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):
    return product_crud.get_products(db) """


@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):

    db_product = product_crud.create_product(db, product)

    if db_product is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return db_product


@router.get("/filter", response_model=list[ProductResponse])
def filter_products(
    category_id: int,
    min_price: float,
    max_price: float,
    db: Session = Depends(get_db)
):
    return product_crud.filter_products(
        db,
        category_id,
        min_price,
        max_price
    )

@router.get("/price/{min_price}", response_model=list[ProductResponse])
def get_products_by_price(
    min_price: float,
    db: Session = Depends(get_db)
):
    return product_crud.get_products_by_price(db, min_price)

@router.get("/with-category/{product_id}")
def get_product_with_category(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "category": {
            "id": product.category.id,
            "name": product.category.name
        }
    }

@router.get("/sort", response_model=list[ProductResponse])
def sort_products(
    order: str = "asc",
    db: Session = Depends(get_db)
):
    return product_crud.sort_products(db, order)

@router.get("/paginate", response_model=list[ProductResponse])
def paginate_products(
    page: int = 1,
    size: int = 5,
    db: Session = Depends(get_db)
):
    return product_crud.get_products_paginated(
        db,
        page,
        size
    )

@router.get("/search", response_model=list[ProductResponse])
def search_products(
    keyword: str,
    db: Session = Depends(get_db)
):
    return product_crud.search_products(
        db,
        keyword
    )

@router.post("/{product_id}/image", response_model=ProductResponse)
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # ---------------------------------------------------------
    # Allowed image types
    # ---------------------------------------------------------

    allowed_content_types = {
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid image type"
        )

    # ---------------------------------------------------------
    # Safe filename
    # ---------------------------------------------------------

    original_filename = Path(
        file.filename or "upload"
    ).name

    extension = Path(
        original_filename
    ).suffix.lower()

    allowed_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file extension"
        )

    # ---------------------------------------------------------
    # Maximum file size = 5 MB
    # ---------------------------------------------------------

    file.file.seek(0, 2)

    file_size = file.file.tell()

    file.file.seek(0)

    max_size = 5 * 1024 * 1024

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File too large"
        )

    # ---------------------------------------------------------
    # Generate safe server-side filename
    # ---------------------------------------------------------

    filename = (
        f"{uuid.uuid4()}_{original_filename}"
    )

    os.makedirs(
        "uploads/products",
        exist_ok=True
    )

    file_path = os.path.join(
        "uploads/products",
        filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    relative_path = (
        f"uploads/products/{filename}"
    )

    product.image_path = relative_path

    db.commit()
    db.refresh(product)

    return product



@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    return product_crud.get_product(
        db,
        product_id
    )


@router.put("/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return product_crud.update_product(
        db,
        product_id,
        product
    )

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return product_crud.delete_product(
        db,
        product_id
    )


@router.get("/", response_model=list[ProductResponse])
def list_products(
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    order: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return product_crud.list_products(
        db=db,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        order=order,
        page=page,
        size=size,
    )