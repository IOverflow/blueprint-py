from bson.objectid import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any, Dict

from src.inmutables import NomenclatureType
import datetime


class PagingModel(BaseModel):
    limit: int = 1000
    skip: int = 0


class Filter(BaseModel):
    field: str
    value: Union[str, List[str]]


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


# ============================================  USER ZONE ==========================================

class Token(BaseModel):
    """
    JWT token representation to use in authentication system
    """
    access_token: str
    token_type: str
    exp: datetime.datetime
    refresh_token: Optional[str] = None
    refresh_exp: Optional[datetime.datetime] = None


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


class RefreshTokenForm(BaseModel):
    refresh_token: str


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
    "nomenclature:read": "Permission to read data about nomenclatures",
    "nomenclature:write": "Permission to create and edit nomenclatures",
    "nomenclature:delete": "Permission to delete nomenclatures",
    "publication-project:read": "Permission to read publication projects",
    "publication-project:write": "Permission to write changes to publication projects",
    "publication-project:commit": "Permission to make changes as commits over publication projects"
}


# ==================================================================================================


# =============================  Nomenclatures  ====================================================

class Nomenclature(Entity):
    Name: str
    type: NomenclatureType
    pattern: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None

    @property
    def has_level(self):
        return self.type == NomenclatureType.type_check_item

    @property
    def has_pattern(self):
        return self.type == NomenclatureType.data_type

    class Config(BaseConfig):
        pass

# ==================================================================================================
