from pydantic import BaseModel


class Category(BaseModel):
    """
    Add category description
    """
    class Config:
        orm_mode = True
