# from nbsapi.api.dependencies.auth import validate_is_authenticated
from typing import List

from fastapi import APIRouter, Depends

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.impact import (
    create_impact_intensity,
    create_impact_unit,
    get_impact_intensities,
    get_impact_units,
    get_impacts,
)
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


@router.post(
    "/impact_intensities",
    response_model=ImpactIntensity,
    dependencies=[Depends(validate_is_authenticated)],
)
async def write_impact_intensity(db_session: DBSessionDep, intensity: ImpactIntensity):
    """Create a new impact intensity measure"""
    targets = await create_impact_intensity(db_session, intensity)
    return targets


@router.get("/impact_units", response_model=List[ImpactUnit])
async def read_impact_unit(db_session: DBSessionDep):
    """Retrieve all available adaptation impact units"""
    target = await get_impact_units(db_session)
    return target


@router.post(
    "/impact_units",
    response_model=ImpactUnit,
    dependencies=[Depends(validate_is_authenticated)],
)
async def write_impact_unit(db_session: DBSessionDep, unit: ImpactUnit):
    """Create a new impact intensity unit"""
    target = await create_impact_unit(db_session, unit)
    return target
