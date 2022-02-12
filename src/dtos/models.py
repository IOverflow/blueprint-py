from bson.objectid import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List


class PagingModel(BaseModel):
    limit: int = 1000
    skip: int = 0


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, oid):
        if not ObjectId.is_valid(oid):
            raise ValueError("Invalid objectid")
        return ObjectId(oid)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseConfig:
    allow_population_by_field_name = True
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}
    orm_mode = True


class Entity(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config(BaseConfig):
        pass


class Category(Entity):
    """
    This is a testing model so we can run a sample project
    """
    name: str
    priority: int = 0
    description: Optional[str] = None

    class Config(Entity.Config):
        # Define an extra configuration
        # for the sake of example in the Swagger
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "My super category",
                "priority": 10,
                "description": "This is an awesome category"
            }
        }


class CategoryWriteDto(BaseModel):
    name: str
    priority: int = 0
    description: Optional[str] = None


# ============================================  USER ZONE ==========================================

class Token(BaseModel):
    """
    JWT token representation to use in authentication system
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


class Role(BaseModel):
    name: str


class User(Entity):
    username: str
    hashed_password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: List[str] = []
    roles: List[Role] = []

    def is_in_role(self, role: str):
        return any(role == r.name for r in self.roles)

    def has_permission(self, permission: str):
        return any(p == permission for p in self.scopes)

    @property
    def is_admin(self):
        return self.is_in_role('Admin')


SCOPES = {
    "users:write": "Permission to edit and create an user",
    "users:read": "Permission to read users data",
    "users:delete": "Permission to delete users",
}

# ==================================================================================================
