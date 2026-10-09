from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings


DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required"
    )


engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
