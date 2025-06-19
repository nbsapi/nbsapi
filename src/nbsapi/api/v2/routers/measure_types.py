"""API endpoints for measure types."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import get_db_session
from nbsapi.crud.measure_type import (
    create_measure_type,
    get_measure_type,
    get_measure_types,
    update_measure_type,
    delete_measure_type,
)
from nbsapi.schemas.measure_type import (
    MeasureTypeCreate,
    MeasureTypeRead,
    MeasureTypeUpdate,
)

router = APIRouter(prefix="/measure_types", tags=["measure_types"])


@router.get("/", response_model=list[MeasureTypeRead])
async def read_measure_types(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve all available measure types."""
    measure_types = await get_measure_types(db, skip=skip, limit=limit)
    return measure_types


@router.get("/{measure_id}", response_model=MeasureTypeRead)
async def read_measure_type(
    measure_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve a specific measure type by ID."""
    measure_type = await get_measure_type(db, measure_id)
    if measure_type is None:
        raise HTTPException(status_code=404, detail="Measure type not found")
    return measure_type


@router.post(
    "/",
    response_model=MeasureTypeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_is_authenticated)],
)
async def create_new_measure_type(
    measure_type: MeasureTypeCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new measure type."""
    # Check if measure type with this ID already exists
    existing = await get_measure_type(db, measure_type.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Measure type with ID {measure_type.id} already exists",
        )

    return await create_measure_type(db, measure_type)


@router.patch(
    "/{measure_id}",
    response_model=MeasureTypeRead,
    dependencies=[Depends(validate_is_authenticated)],
)
async def update_existing_measure_type(
    measure_id: str,
    measure_type_update: MeasureTypeUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update an existing measure type."""
    updated = await update_measure_type(db, measure_id, measure_type_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Measure type not found")
    return updated


@router.delete(
    "/{measure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(validate_is_authenticated)],
    responses={
        204: {"description": "Measure type deleted successfully"},
        404: {"description": "Measure type not found"},
        409: {
            "description": "Cannot delete: measure type is referenced by other resources"
        },
    },
)
async def delete_existing_measure_type(
    measure_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a measure type."""
    deleted = await delete_measure_type(db, measure_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Measure type not found")
