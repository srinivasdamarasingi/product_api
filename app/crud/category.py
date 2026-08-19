from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.categories import CategoryCreate
from sqlalchemy.exc import IntegrityError


""" def create_category(db: Session, category: CategoryCreate):
    db_category = Category(
        name=category.name
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category """

def create_category(db, category):

    db_category = Category(
        name=category.name
    )

    db.add(db_category)

    try:
        db.commit()
        db.refresh(db_category)

        return db_category

    except IntegrityError:

        db.rollback()

        return None


def get_categories(db: Session):
    return db.query(Category).all()


def get_category(db: Session, category_id: int):
    return db.query(Category).filter(
        Category.id == category_id
    ).first()

