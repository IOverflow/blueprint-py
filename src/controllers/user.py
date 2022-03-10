from typing import List, Optional

from fastapi import APIRouter, Path, Security, status, Depends, Body

from src.dependencies import get_filters
from src.dtos.viewmodels import (UserAdminViewModel,
                                 CreatedUserAdminViewModel,
                                 CreateUserRequestModel, UpdateUserRequestModel,
                                 Response, Page, LoggedUser)
from src.dtos.models import User, Filter
from src.services.crypto import RoleAuth, adminRole, anyRole
from src.services.service_adapter import UserService, PagingModel
from .routers import ApiController

router = ApiController(prefix="/user", tags=["Users"])
service = UserService()


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


@router.get('/admin/{id}', response_model=Response[UserAdminViewModel])
async def get_user_as_admin(
        id: str = Path(...),
        user: LoggedUser = Security(adminRole, scopes=["users:read"])
):
    """
    Gets an user representation for displaying in a view in an admin
    view. This representation only gets displayed by if the logged in
    user is an admin and has read access over users.
    """
    requested_user = await service.get(id)
    if requested_user is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, message="User not found")
    return Response(data=requested_user)


@router.get('/admin', response_model=Response[Page[UserAdminViewModel]])
async def list_users_as_admin(
        paging: PagingModel = Depends(),
        filters: Optional[List[Filter]] = Depends(get_filters),
        user: LoggedUser = Security(adminRole, scopes=["users:read"])
):
    """
    Gets the list of users with an extended field representation.
    This endpoint is meant for admins with read access over the
    users.
    """
    users = await service.get(paging=paging, filters=filters)
    total = await service.count()
    return Response(data=Page(items=users, total=total, records=len(users)))


@router.post('/admin', response_model=Response[CreatedUserAdminViewModel])
async def create_user_as_admin(
        model: CreateUserRequestModel = Body(...),
        user: LoggedUser = Security(adminRole, scopes=["users:write"])
):
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
    password = RoleAuth.generate_strong_password()
    data['hashed_password'] = RoleAuth.get_password_hash(password)
    _id = await service.add(data)
    return Response(
        data=CreatedUserAdminViewModel(id=_id, password=password),
        status_code=status.HTTP_201_CREATED
    )


@router.delete('/admin/{id}', response_model=Response[str])
async def delete_user_as_admin(
        id: str = Path(...),
        user: LoggedUser = Security(adminRole, scopes=['users:delete'])
):
    """
    Deletes an user from the system. It requires "users:delete" permission
    and an admin Role
    """
    if await service.delete(id):
        return Response(message="Delete successfully", data=id, status_code=status.HTTP_202_ACCEPTED)

    return Response(message="User could not been deleted", status=status.HTTP_400_BAD_REQUEST)


@router.put('/admin/{id}', response_model=Response[UserAdminViewModel])
async def update_user_as_admin(
        id: str = Path(...),
        model: UpdateUserRequestModel = Body(...),
        user: LoggedUser = Security(adminRole, scopes=['users:write'])
):
    """
    Updates an user information. Requires an admin with "users:write"
    permissions
    """
    if await service.update(id, model.dict(exclude_unset=True)):
        new_user = await service.get(id)
        return Response(data=new_user, status_code=status.HTTP_201_CREATED)

    return Response(status_code=status.HTTP_400_BAD_REQUEST, message="Failed to update user")
