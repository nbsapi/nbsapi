from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nbsapi.models import User as UserDBModel


async def get_user(db_session: AsyncSession, user_id: int):
    user = (
        await db_session.scalars(select(UserDBModel).where(UserDBModel.id == user_id))
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_by_email(db_session: AsyncSession, email: str):
    return (
        await db_session.scalars(select(UserDBModel).where(UserDBModel.email == email))
    ).first()
