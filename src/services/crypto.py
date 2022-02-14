from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from src.dataaccess.repository.repository import UserRepository
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from decouple import config
from fastapi import HTTPException, status, Depends
from src.dtos.models import TokenData, SCOPES
from pydantic import ValidationError
from random import sample, randint
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/token", scopes=SCOPES)


class CryptoService:
    # Allow for Dependency Injection so we can test this
    # service without a database
    def __init__(self, repo=UserRepository()):
        self._user_repo = repo

    @staticmethod
    def generate_strong_password():
        all_characters = string.ascii_lowercase + string.ascii_uppercase + string.punctuation + string.digits
        length = randint(8, 12)
        return "".join(sample(all_characters, length))

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


class RoleAuth(CryptoService):
    def __init__(self, allowed_roles: List[str] = None):
        super(RoleAuth, self).__init__()
        self.allowed_roles = allowed_roles

    async def __call__(self, security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        else:
            authenticate_value = f'Bearer'

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

        try:
            payload = jwt.decode(token, config("SECRET_JWT_KEY"), algorithms=[jwt.ALGORITHMS.HS256])
            # username must come as subject
            username: str = payload.get('sub')
            if username is None:
                raise credentials_exception
            token_scopes = payload.get('scopes', [])
            token_data = TokenData(username=username, scopes=token_scopes)
        except (JWTError, ValidationError):
            raise credentials_exception

        if (user := await self._user_repo.get_by_username(username=token_data.username)) is None:
            raise credentials_exception

        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )

        # Check the roles
        if not self.allowed_roles or any(role.name in self.allowed_roles for role in user.roles):
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed user role.",
        )


adminRole = RoleAuth(['Admin'])
anyRole = RoleAuth()