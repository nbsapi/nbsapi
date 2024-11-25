# from nbsapi.api.dependencies.auth import validate_is_authenticated
from typing import List

from fastapi import APIRouter, Depends

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.impact import get_impact_intensities, get_impact_units, get_impacts
from nbsapi.schemas.impact import ImpactBase, ImpactIntensity, ImpactUnit

router = APIRouter(
    prefix="/api/impacts",
    tags=["impacts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/impacts", response_model=List[ImpactBase])
async def read_impacts(db_session: DBSessionDep):
    """Retrieve all available adaptation impacts"""
    targets = await get_impacts(db_session)
    return targets


@router.get("/impact_intensities", response_model=List[ImpactIntensity])
async def read_impact_intensity(db_session: DBSessionDep):
    """Retrieve all available adaptation impact intensities"""
    targets = await get_impact_intensities(db_session)
    return targets


@router.get("/impact_units", response_model=List[ImpactUnit])
async def read_impact_unit(db_session: DBSessionDep):
    """Retrieve all available adaptation impact units"""
    targets = await get_impact_units(db_session)
    return targets
