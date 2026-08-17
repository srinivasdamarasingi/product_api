from pydantic import BaseModel, ConfigDict



class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    category_id: int
    image_path: str | None = None



class ProductUpdate(BaseModel):
    name: str
    price: float
    stock: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    category_id: int
    image_path: str | None = None

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)