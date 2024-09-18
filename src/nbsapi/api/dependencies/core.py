from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nbsapi.database import get_db_session

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]