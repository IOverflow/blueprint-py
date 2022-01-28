from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from src.dataaccess.repository.repository import UserRepository
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from decouple import config
from fastapi import HTTPException, status, Depends
from src.dtos.models import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


class CryptoService:
    # Allow for Dependency Injection so we can test this
    # service without a database
    def __init__(self, repo=UserRepository()):
        self._user_repo = repo

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    async def authenticate_user(self, username: str, password: str):
        if (user := await self._user_repo.get_by_username(username)) is not None:
            if not CryptoService.verify_password(password, user.hashed_password):
                return False
            return user
        return False
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta]):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)

        # to_encode holds our claims. Add an expiration
        # time in there
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, config("SECRET_JWT_KEY"), algorithm=jwt.ALGORITHMS.HS256)
        return encoded_jwt

    async def _get_current_user(self, token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, config("SECRET_JWT_KEY"), algorithms=[jwt.ALGORITHMS.HS256])
            # username must come as subject
            username: str = payload.get('sub')
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception

        if (user := await self._user_repo.get_by_username(username=token_data.username)) is None:
            raise credentials_exception
        return user

    async def __call__(self, token: str = Depends(oauth2_scheme)):
        return await self._get_current_user(token)
