from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.category import Category

from app.models.products import Product
from app.schemas.products import (
    ProductCreate,
    ProductUpdate
)

from app.models.products import Product
from fastapi import HTTPException
from app.exceptions.custom_exceptions import ProductNotFoundException
from app.schemas.products import ProductResponse
from app.services.redis_service import redis_client
import json



def create_product(
    db: Session,
    product: ProductCreate
):
    category = db.query(Category).filter(
        Category.id == product.category_id
    ).first()

    if not category:
        return None
    
    new_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

def get_products(db: Session):
    products = db.scalars(
        select(Product)
    ).all()

    return products

def get_product(db: Session, product_id: int):

    print("1. Function Started")

    cache_key = f"product:{product_id}"

    cached_product = redis_client.get(cache_key)

    print("2. Redis Read:", cached_product)

    if cached_product:
        print("3. ✅ Cache Hit")
        data = json.loads(cached_product)
        return ProductResponse(**data)

    print("4. ❌ Cache Miss")

    product = db.scalar(
        select(Product).where(Product.id == product_id)
    )

    print("5. Database Result:", product)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    response = ProductResponse.model_validate(product)

    print("6. Before Redis Save")

    redis_client.setex(
    cache_key,
    300,
    response.model_dump_json()
)

    print("Saved to Redis")

    # Read it back immediately
    value = redis_client.get(cache_key)
    print("Immediately read:", value)

    return response

def update_product(
    db: Session,
    product_id: int,
    product: ProductUpdate
):
    existing_product = db.scalar(
        select(Product).where(Product.id == product_id)
    )

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.stock = product.stock

    db.commit()
    db.refresh(existing_product)

    return existing_product


def delete_product(
    db: Session,
    product_id: int
):
    product = db.scalar(
        select(Product).where(Product.id == product_id)
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }

def get_products_by_price(db: Session, min_price: float):
    return (
        db.query(Product)
        .filter(Product.price >= min_price)
        .all()
    )

def filter_products(
    db: Session,
    category_id: int,
    min_price: float,
    max_price: float
):
    return (
        db.query(Product)
        .filter(
            Product.category_id == category_id,
            Product.price >= min_price,
            Product.price <= max_price
        )
        .all()
    )

def sort_products(db: Session, order: str):

    if order.lower() == "desc":
        return (
            db.query(Product)
            .order_by(Product.price.desc())
            .all()
        )

    return (
        db.query(Product)
        .order_by(Product.price.asc())
        .all()
    )

def get_products_paginated(
    db: Session,
    page: int,
    size: int
):
    offset = (page - 1) * size

    return (
        db.query(Product)
        .offset(offset)
        .limit(size)
        .all()
    )

def search_products(
    db: Session,
    keyword: str
):
    return (
        db.query(Product)
        .filter(
            Product.name.ilike(f"%{keyword}%")
        )
        .all()
    )

def list_products(
    db: Session,
    keyword: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    order: str = "asc",
    page: int = 1,
    size: int = 5,
):
    query = db.query(Product)

    if keyword:
        query = query.filter(Product.name.ilike(f"%{keyword}%"))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if order.lower() == "desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.price.asc())

    offset = (page - 1) * size

    return (
        query
        .offset(offset)
        .limit(size)
        .all()
    )