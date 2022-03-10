from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from src.dtos.models import Token, RefreshTokenForm, SCOPES
from src.services.crypto import CryptoService
from datetime import timedelta, datetime
from typing import List
from .routers import ApiController

router = ApiController(prefix="/account", tags=["Account"])
crypt_service = CryptoService()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await crypt_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_requested_scopes = list(set(user.scopes).intersection(set(form_data.scopes)))
    access_token_expires = timedelta(minutes=60)
    refresh_token_expires = timedelta(days=31)
    access_token = CryptoService.create_access_token(
        data={
            "sub": user.username,
            "scopes": user_requested_scopes,
            "roles": list(role.name for role in user.roles),
            "full_name": user.full_name,
            "email": user.email
        },
        expires_delta=access_token_expires
    )
    refresh_token = CryptoService.create_access_token(
        data={
            "sub": user.username,
            "scopes": user_requested_scopes,
            "roles": list(role.name for role in user.roles),
            "full_name": user.full_name,
            "email": user.email
        },
        expires_delta=refresh_token_expires,
        refresh=True
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "exp": datetime.utcnow() + access_token_expires,
        "refresh_token": refresh_token,
        "refresh_exp": datetime.utcnow() + refresh_token_expires,
    }


@router.post("/refresh_token", response_model=Token)
async def refresh_access_token(refresh_token_form: RefreshTokenForm = Body(...)):
    user = await crypt_service.get_current_user(refresh_token_form.refresh_token, refresh=True)
    scopes = CryptoService.get_scopes_from_refresh(refresh_token_form.refresh_token)
    access_token_expires = timedelta(minutes=60)

    new_access_token = crypt_service.create_access_token(
        data={
            "sub": user.username,
            "scopes": scopes,
            "roles": list(role.name for role in user.roles),
            "full_name": user.full_name,
            "email": user.email
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "exp": datetime.utcnow() + access_token_expires,
    }


@router.get('/permissions', response_model=List[str])
def get_available_permissions():
    """
    List the available permissions in the system an user can ask for when
    signing in.
    System handles login and assign each user the intersection between its
    assigned permissions and the asked permissions.
    """
    return list(SCOPES.keys())
