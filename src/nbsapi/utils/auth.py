from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer

# from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nbsapi.config import settings
from nbsapi.models import User
from nbsapi.schemas.user import UserWrite

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


ACCESS_TOKEN_SECRET_KEY = settings.oauth_token_secret
ACCESS_TOKEN_ALGORITHM = "HS256"  # noqa: S105


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        bytes(password, encoding="utf-8"),
        bcrypt.gensalt(),
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        bytes(plain_password, encoding="utf-8"),
        bytes(hashed_password, encoding="utf-8"),
    )


async def create_user(db_session: AsyncSession, user: UserWrite):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        disabled=False,
    )
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user


async def is_authenticated(db_session: AsyncSession, username: str, password: str):
    user = (
        await db_session.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def decode_jwt(token: str) -> dict:
    return jwt.decode(
        token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ACCESS_TOKEN_ALGORITHM]
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ACCESS_TOKEN_ALGORITHM
    )
    return encoded_jwt
