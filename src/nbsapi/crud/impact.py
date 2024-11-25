from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nbsapi.models.impact import Impact
from nbsapi.models.impact_intensity import ImpactIntensity as IIM
from nbsapi.models.impact_unit import ImpactUnit as IIU
from nbsapi.schemas.impact import ImpactBase, ImpactIntensity, ImpactUnit


async def get_impacts(db_session: AsyncSession):
    """Retrieve all available adaptation impacts"""
    impacts = (await db_session.scalars(select(Impact))).unique()
    actual = [
        ImpactBase(
            magnitude=impact.magnitude, unit=impact.unit, intensity=impact.intensity
        )
        for impact in impacts
    ]
    return actual


async def get_impact_intensities(db_session: AsyncSession):
    """Retrieve all available impact intensities"""
    intensities = (await db_session.scalars(select(IIM))).unique()
    actual = [
        ImpactIntensity(intensity=intensity.intensity) for intensity in intensities
    ]
    return actual


async def get_impact_units(db_session: AsyncSession):
    """Retrieve all available impact units"""
    units = (await db_session.scalars(select(IIU))).unique()
    actual = [
        ImpactUnit(unit=unit.unit, description=unit.description) for unit in units
    ]
    return actual
