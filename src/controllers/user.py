from typing import Optional

from fastapi import Security, status, Depends, Body

from src.dependencies import get_filters, get_user_from_request
from src.dtos.viewmodels import (
    UserAdminViewModel,
    CreatedUserAdminViewModel,
    CreateUserRequestModel, UpdateUserRequestModel,
    Response, Page, LoggedUser
)
from src.dtos.models import User, PagingModel
from src.services.crypto import adminRole, anyRole, CryptoService
from .routers import ApiController

router = ApiController(prefix="/user", tags=["Users"])


@router.get('', response_model=Response[LoggedUser])
def get_user(user: LoggedUser = Security(anyRole, scopes=["users:read"])):
    """
    Gets an user representation for displaying in a view. This
    data is striped from user sensitive information, such as
    encrypted password, roles and permissions. This is meant to be used as an endpoint
    for querying user profile info. This endpoint only depends on the
    "users:read" scope, which most users should have.
    """
    return Response(data=user)


@router.get(
    '/admin/{id}',
    response_model=Response[UserAdminViewModel],
    dependencies=[Security(adminRole, scopes=["users:read"])]
)
async def get_user_as_admin(user: Optional[User] = Depends(get_user_from_request)):
    """
    Gets an user representation for displaying in a view in an admin
    view. This representation only gets displayed by if the logged in
    user is an admin and has read access over users.
    """
    if user is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, message="User not found")
    return Response(data=user)


@router.get(
    '/admin',
    response_model=Response[Page[UserAdminViewModel]],
    dependencies=[Security(adminRole, scopes=["users:read"])]
)
async def list_users_as_admin(paging: PagingModel = Depends(), filters: dict = Depends(get_filters)):
    """
    Gets the list of users with an extended field representation.
    This endpoint is meant for admins with read access over the
    users.
    """
    filters = {f.field: f.value for f in filters}
    users = await User.find(filters).skip(paging.skip).limit(paging.limit).to_list()
    total = await User.find(filters).count()
    return Response(data=Page(items=users, total=total, records=len(users)))


@router.post(
    '/admin',
    response_model=Response[CreatedUserAdminViewModel],
    dependencies=[Security(adminRole, scopes=["users:write"])]
)
async def create_user_as_admin(model: CreateUserRequestModel = Body(...)):
    """
    Creates a new user in the system. The caller of this
    endpoint must be an admin with write access privileges
    over the users entity. A new strong password is generated
    for the user and sent with the new id of the user. This
    password must be saved because it would not be showed
    again, and it is not stored in plain text in the database.
    """
    data = model.dict(exclude_unset=True)
    # autogenerate a strong password
    password = CryptoService.generate_strong_password()
    data['hashed_password'] = CryptoService.get_password_hash(password)
    user = await User(**data).insert()
    return Response(
        data=CreatedUserAdminViewModel(id=user.id, password=password),
        status_code=status.HTTP_201_CREATED
    )


@router.delete(
    '/admin/{id}',
    response_model=Response[str],
    dependencies=[Security(adminRole, scopes=['users:delete'])]
)
async def delete_user_as_admin(user: User = Depends(get_user_from_request)):
    """
    Deletes an user from the system. It requires "users:delete" permission
    and an admin Role
    """
    if user is not None:
        if (await user.delete()).deleted_count == 1:
            return Response(message="Delete successfully", data=id, status_code=status.HTTP_202_ACCEPTED)

    return Response(message="User could not been deleted", status_code=status.HTTP_400_BAD_REQUEST)


@router.patch(
    '/admin/{id}',
    response_model=Response[UserAdminViewModel],
    dependencies=[Security(adminRole, scopes=['users:write'])]
)
async def update_user_as_admin(
        user: Optional[User] = Depends(get_user_from_request),
        model: UpdateUserRequestModel = Body(...),
):
    """
    Updates an user information. Requires an admin with "users:write"
    permissions
    """
    if user is not None:
        await user.set(model.dict(exclude_unset=True))
        return Response(data=user, status_code=status.HTTP_201_CREATED)

    return Response(status_code=status.HTTP_400_BAD_REQUEST, message="Failed to update user")
