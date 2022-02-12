from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.dtos.models import Token
from src.dependencies import crypto_service
from src.services.crypto import CryptoService
from datetime import timedelta

router = APIRouter(prefix="/account", tags=["Account"])


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 crypt_service: CryptoService = Depends(crypto_service)):
    user = await crypt_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_requested_scopes = list(set(user.scopes).intersection(set(form_data.scopes)))
    access_token_expires = timedelta(minutes=60)
    access_token = CryptoService.create_access_token(
        data={"sub": user.username, "scopes": user_requested_scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
