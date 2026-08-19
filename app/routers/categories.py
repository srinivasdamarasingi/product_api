from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.categories import CategoryCreate, CategoryResponse
from app.crud import category as category_crud

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


""" @router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return category_crud.create_category(db, category) """

@router.post("/")
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):

    db_category = category_crud.create_category(
        db,
        category
    )

    if db_category is None:
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    return db_category

@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return category_crud.get_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = category_crud.get_category(db, category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category