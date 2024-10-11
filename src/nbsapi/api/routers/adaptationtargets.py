# from nbsapi.api.dependencies.auth import validate_is_authenticated
from typing import List

from fastapi import APIRouter, Depends

from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.adaptationtarget import create_target, get_target, get_targets
from nbsapi.schemas.adaptationtarget import TargetBase

router = APIRouter(
    prefix="/api/targets",
    tags=["targets"],
    responses={404: {"description": "Not found"}},
)


@router.get("/target", response_model=List[TargetBase])
async def read_targets(db_session: DBSessionDep):
    """Retrieve all available adaptation targets"""
    targets = await get_targets(db_session)
    return targets


@router.post("/target", response_model=TargetBase)
async def write_target(db_session: DBSessionDep, itarget: TargetBase):
    """Create a new adaptation target"""
    wtarget = await create_target(db_session, itarget=itarget)
    return wtarget
