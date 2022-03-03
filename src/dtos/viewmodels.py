from pydantic import BaseModel, Field
from typing import Optional, List, TypeVar, Generic, Sequence

from pydantic.generics import GenericModel

from .models import Role, PyObjectId, BaseConfig
from src.inmutables import NomenclatureType


# =================================   USERS VIEW MODELS  ============================= #
class LoggedUser(BaseModel):
    username: str
    scopes: List[str]
    roles: List[str]
    email: Optional[str] = None
    full_name: Optional[str] = None

    class Config(BaseConfig):
        pass


class UserAdminViewModel(LoggedUser):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    scopes: List[str] = []
    roles: List[Role] = []


class CreatedUserAdminViewModel(BaseModel):
    password: str = Field(description="A one time only show of the user password when it is created")
    id: PyObjectId = Field(description="Id of the newly created user, so it is easy to access its data")

    class Config(BaseConfig):
        pass


class CreateUserRequestModel(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: List[str] = []
    roles: List[Role] = []

    class Config(BaseConfig):
        pass


class UpdateUserRequestModel(BaseModel):
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: Optional[List[str]] = None
    roles: Optional[List[Role]] = None


# =================================  ==================  ============================== #

# =================================  NOMENCLATURES VIEW MODELS  ======================= #
class NomenclatureForm(BaseModel):
    Name: str
    type: NomenclatureType
    pattern: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None


class NomenclatureViewModel(BaseModel):
    id: PyObjectId = Field(alias='_id')
    Name: str
    has_level: bool = True
    has_pattern: bool = True
    type: NomenclatureType
    pattern: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None

    class Config(BaseConfig):
        pass


# ===================================================================================== #


# ===============================    RESPONSES    =================================== #

T = TypeVar('T')


class Response(GenericModel, Generic[T]):
    data: Optional[T] = None
    message: str = "Success"
    status_code: int = 200

    class Config(BaseConfig):
        pass


class Page(GenericModel, Generic[T]):
    items: Sequence[T] = []
    records: int = 0
    total: int = 0

    class Config:
        orm_mode = True


class NomenclatureTypeViewModel(BaseModel):
    label: str
    value: str
    has_level: bool
    has_pattern: bool

    class Config:
        orm_mode = True
# =================================================================================== #
