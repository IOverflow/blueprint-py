from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from decouple import config
from fastapi import HTTPException, status, Depends
from src.dtos.models import TokenData, SCOPES, User
from pydantic import ValidationError
from random import sample, randint
import string

from src.dtos.viewmodels import LoggedUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/account/token", scopes=SCOPES)


class CryptoService:
    # Allow for Dependency Injection so we can test this
    # service without a database

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

    @staticmethod
    async def authenticate_user(username: str, password: str):
        if (user := await User.find_one(User.username == username)) is not None:
            if not CryptoService.verify_password(password, user.hashed_password):
                return False
            return user
        return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta], refresh=False):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow()

        # to_encode holds our claims. Add an expiration
        # time in there
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            to_encode,
            config("SECRET_JWT_KEY") if not refresh else config("SECRET_REFRESH_JWT_KEY"),
            algorithm=jwt.ALGORITHMS.HS256
        )
        return encoded_jwt

    @staticmethod
    def get_scopes_from_refresh(refresh_token):
        payload = jwt.decode(
            refresh_token,
            config("SECRET_REFRESH_JWT_KEY"),
            algorithms=[jwt.ALGORITHMS.HS256]
        )
        scopes = payload.get('scopes') or []
        return scopes

    @staticmethod
    async def get_current_user(token: str, refresh: bool = False):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token,
                config("SECRET_JWT_KEY") if not refresh else config("SECRET_REFRESH_JWT_KEY"),
                algorithms=[jwt.ALGORITHMS.HS256]
            )
            # username must come as subject
            username: str = payload.get('sub')
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError as e:
            raise credentials_exception

        if (user := await User.find_one(User.username == token_data.username)) is None:
            raise credentials_exception
        return user


class RoleAuth:
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
            token_roles = payload.get('roles', [])
            token_full_name = payload.get('full_name')
            token_email = payload.get('email')
            token_language = payload.get('lang', 'en')
        except (JWTError, ValidationError):
            raise credentials_exception

        for scope in security_scopes.scopes:
            if scope not in token_scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )

        # Check the roles
        if not self.allowed_roles or any(role in self.allowed_roles for role in token_roles):
            # Add to user only the scopes it has been granted permission for
            return LoggedUser(
                username=username,
                roles=token_roles,
                scopes=token_scopes,
                full_name=token_full_name,
                email=token_email
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed user role.",
        )


adminRole = RoleAuth(['Admin'])
anyRole = RoleAuth()
