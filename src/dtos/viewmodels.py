from pydantic import BaseModel, Field
from typing import Optional, List
from .models import Role, PyObjectId, BaseConfig


# =================================   USERS VIEW MODELS  ============================= #
class UserReadDto(BaseModel):
    username: str
    id: Optional[PyObjectId] = Field(default=None)
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    class Config(BaseConfig):
        pass


class UserAdminViewModel(UserReadDto):
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


# ===============================    RESPONSES    =================================== #
class Response(BaseModel):
    data: Optional[object] = None
    message: str = "Success"
    status_code: int = 200

    class Config(BaseConfig):
        pass


class UserResponse(Response):
    data: Optional[UserReadDto] = None


class UserListResponse(Response):
    data: List[UserReadDto] = []


class UserAdminViewModelResponse(Response):
    data: Optional[UserAdminViewModel] = None


class UserAdminViewModelListResponse(Response):
    data: List[UserAdminViewModel] = []


class CreatedUserAdminViewModelResponse(Response):
    data: Optional[CreatedUserAdminViewModel] = None
# =================================================================================== #
