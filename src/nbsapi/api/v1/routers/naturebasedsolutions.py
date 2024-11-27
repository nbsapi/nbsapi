# from nbsapi.api.dependencies.auth import validate_is_authenticated

import json
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.naturebasedsolution import (
    create_nature_based_solution,
    get_filtered_solutions,
    get_solution,
)
from nbsapi.schemas.adaptationtarget import AdaptationTargetRead
from nbsapi.schemas.impact import ImpactIntensity
from nbsapi.schemas.naturebasedsolution import (
    NatureBasedSolutionCreate,
    NatureBasedSolutionRead,
)

router = APIRouter(
    prefix="/api/solutions",
    tags=["solutions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/solutions/{solution_id}", response_model=NatureBasedSolutionRead)
async def read_nature_based_solution(solution_id: int, db_session: DBSessionDep):
    """Retrieve a nature-based solution using its ID"""
    solution = await get_solution(db_session, solution_id)
    return solution


@router.get(
    "/solutions",
    response_model=List[NatureBasedSolutionRead],
)
async def get_solutions(
    db_session: DBSessionDep,
    targets: Optional[str] = Query(
        None,
        description=(
            "JSON string representing a list of adaptation targets to filter by. "
            'Example: `[{"adaptation": {"type": "Heat"}, "value": 80}]`'
        ),
    ),
    intensities: Optional[str] = Query(
        None,
        description=(
            "JSON string representing a list of impact intensities to filter by. "
            'Example: `[{"intensity":"low"}]`'
        ),
    ),
    bbox: Optional[List[float]] = Query(
        None,
        description=(
            "Bounding box specified as `[west, south, east, north]`. "
            "Example: `[-6.2757665, 53.332055, -6.274319, 53.332553]`. Must cover a max area of 1 sq km."
        ),
    ),
):
    """
    Return a list of nature-based solutions using _optional_ filter criteria:

    - `targets`: A JSON string representing an array of one or more **adaptation targets**.
    - `bbox`: An array of 4 EPSG 4326 coordinates. Only solutions intersected by the bbox will be returned. It must be **<=** 1 km sq.
    - `intensities`: A JSON string representing an array of one or more **impact intensities**.
    """
    # Parse and validate `targets`
    parsed_targets = None
    if targets:
        try:
            target_list = json.loads(targets)  # Parse the JSON string
            if not isinstance(target_list, list):
                raise ValueError("`targets` must be a JSON array.")
            parsed_targets = [
                AdaptationTargetRead(**item) for item in target_list
            ]  # Validate using Pydantic
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid targets format: {str(e)}"
            )

    # Parse and validate `intensities`
    parsed_intensities = None
    if intensities:
        try:
            intensity_list = json.loads(intensities)  # Parse the JSON string
            if not isinstance(intensity_list, list):
                raise ValueError("`intensities` must be a JSON array.")
            parsed_intensities = [
                ImpactIntensity(**item) for item in intensity_list
            ]  # Validate using Pydantic
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid intensities format: {str(e)}"
            )
        print(parsed_intensities)

    # Validate bbox
    if bbox:
        if len(bbox) != 4:
            raise HTTPException(
                status_code=400,
                detail="Bounding box must contain exactly 4 float values.",
            )
        west, south, east, north = bbox
        if not (-180 <= west <= 180):
            raise HTTPException(
                status_code=400,
                detail="West value must be between -180 and 180 degrees.",
            )
        if not (-90 <= south <= 90):
            raise HTTPException(
                status_code=400,
                detail="South value must be between -90 and 90 degrees.",
            )
        if not (-180 <= east <= 180):
            raise HTTPException(
                status_code=400,
                detail="East value must be between -180 and 180 degrees.",
            )
        if not (-90 <= north <= 90):
            raise HTTPException(
                status_code=400,
                detail="North value must be between -90 and 90 degrees.",
            )

    # Fetch solutions using validated inputs
    solutions = await get_filtered_solutions(
        db_session, parsed_targets, bbox, parsed_intensities
    )
    return solutions


@router.post(
    "/add_solution/",
    response_model=NatureBasedSolutionRead,
    dependencies=[Depends(validate_is_authenticated)],
)
async def write_nature_based_solution(
    solution: NatureBasedSolutionCreate, db_session: DBSessionDep
):
    """
    Add a nature-based solution. The payload must be a `NatureBasedSolutionRead` object.
    Its `adaptations` array must contain one or more valid `AdaptationTargetRead` objects

    """
    solution = await create_nature_based_solution(db_session, solution)
    return solution
