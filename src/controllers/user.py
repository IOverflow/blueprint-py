from fastapi import APIRouter, Path, Security, status, Depends, Body
from src.dtos.viewmodels import (UserResponse, UserAdminViewModelListResponse, UserAdminViewModel,
                                 CreatedUserAdminViewModelResponse, CreatedUserAdminViewModel, UserReadDto,
                                 CreateUserRequestModel, UserAdminViewModelResponse, UpdateUserRequestModel,
                                 Response)
from src.dtos.models import User
from src.services.crypto import RoleAuth, adminRole, anyRole
from src.services.service_adapter import UserService, PagingModel

router = APIRouter(prefix="/user", tags=["Users"])
service = UserService()


@router.get('', response_model=UserResponse)
def get_user(user: User = Security(anyRole, scopes=["users:read"])):
    """
    Gets an user representation for displaying in a view. This
    data is striped from user sensitive information, such as
    encrypted password, roles and permissions. This is meant to be used as an endpoint
    for querying user profile info. This endpoint only depends on the
    "users:read" scope, which must users should have.
    """
    user_view_model = UserReadDto.from_orm(user)
    return UserResponse(data=user_view_model)


@router.get('/admin/{id}', response_model=UserAdminViewModelResponse)
async def get_user_as_admin(
        id: str = Path(...),
        user: User = Security(adminRole, scopes=["users:read"])
):
    """
    Gets an user representation for displaying in a view in an admin
    view. This representation only gets displayed by if the logged in
    user is an admin and has read access over users.
    """
    requested_user = await service.get(id)
    if requested_user is None:
        return UserAdminViewModelResponse(status_code=status.HTTP_404_NOT_FOUND, message="User not found")
    return UserAdminViewModelResponse(data=requested_user)


@router.get('/admin', response_model=UserAdminViewModelListResponse)
async def list_users_as_admin(
        paging: PagingModel = Depends(),
        user: User = Security(adminRole, scopes=["users:read"])
):
    """
    Gets the list of users with an extended field representation.
    This endpoint is meant for admins with read access over the
    users.
    """
    users = await service.get(paging=paging)
    return UserAdminViewModelListResponse(data=users)


@router.post('/admin', response_model=CreatedUserAdminViewModelResponse)
async def create_user_as_admin(
        model: CreateUserRequestModel = Body(...),
        user: User = Security(adminRole, scopes=["users:write"])
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
    return CreatedUserAdminViewModelResponse(
        data=CreatedUserAdminViewModel(id=_id, password=password),
        status_code=status.HTTP_201_CREATED
    )


@router.delete('/admin/{id}', response_model=Response)
async def delete_user_as_admin(
        id: str = Path(...),
        user: User = Security(adminRole, scopes=['users:delete'])
):
    """
    Deletes an user from the system. It requires "users:delete" permission
    and an admin Role
    """
    if await service.delete(id):
        return Response(message="Delete successfully", data=id, status_code=status.HTTP_202_ACCEPTED)

    return Response(message="User could not been deleted", status=status.HTTP_400_BAD_REQUEST)


@router.put('/admin/{id}', response_model=UserAdminViewModelResponse)
async def update_user_as_admin(
        id: str = Path(...),
        model: UpdateUserRequestModel = Body(...),
        user: User = Security(adminRole, scopes=['users:write'])
):
    """
    Updates an user information. Requires an admin with "users:write"
    permissions
    """
    if await service.update(id, model.dict(exclude_unset=True)):
        new_user = await service.get(id)
        return UserAdminViewModelResponse(data=new_user, status_code=status.HTTP_201_CREATED)

    return UserAdminViewModelResponse(status_code=status.HTTP_400_BAD_REQUEST, message="Failed to update user")
