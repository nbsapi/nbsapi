# from nbsapi.api.dependencies.auth import validate_is_authenticated

from typing import List, Optional

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, ConfigDict, Field, model_validator

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.naturebasedsolution import (
    create_nature_based_solution,
    get_filtered_solutions,
    get_solution,
)
from nbsapi.schemas.adaptationtarget import AdaptationTargetRead
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


# Define a schema for the request body
class SolutionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "bbox": [-6.2757665, 53.332055, -6.274319, 53.332553],
                    "adaptation": {"type": "Heat", "value": 10},
                }
            ]
        }
    )
    targets: Optional[List["AdaptationTargetRead"]] = Body(
        None, description="List of adaptation targets to filter by"
    )
    bbox: Optional[List[float]] = Field(
        None,
        description="Bounding box specified as [west, south, east, north]. The list should contain exactly four float values. Max 1 sq km",
        min_length=4,
        max_length=4,
    )

    @model_validator(mode="before")
    def check_bbox(cls, values):
        bbox = values.get("bbox")
        if bbox:
            if len(bbox) != 4:
                raise ValueError(
                    "Bounding box must contain exactly 4 float values: [west, south, east, north]"
                )
            west, south, east, north = bbox
            # Validate the geographic ranges
            if not (-180 <= west <= 180):
                raise ValueError("West value must be between -180 and 180 degrees")
            if not (-90 <= south <= 90):
                raise ValueError("South value must be between -90 and 90 degrees")
            if not (-180 <= east <= 180):
                raise ValueError("East value must be between -180 and 180 degrees")
            if not (-90 <= north <= 90):
                raise ValueError("North value must be between -90 and 90 degrees")
        return values


# Route definition
@router.post(
    "/solutions",
    response_model=List[NatureBasedSolutionRead],
)
async def get_solutions(
    db_session: DBSessionDep,
    request_body: Optional[SolutionRequest] = Body(None),
):
    """
    Return a list of nature-based solutions using _optional_ filter criteria:

    - `targets`: An array of one or more **adaptation targets** and their associated protection values. Solutions having targets with protection values **equal to or greater than** the specified values will be returned
    - `bbox`: An array of 4 EPSG 4326 coordinates: `[xmin, ymin, xmax, ymax]` / `[west, south, east, north]` Only solutions intersected by the bbox will be returned. It must be **<=** 1 km sq

    """
    targets = request_body.targets if request_body else None
    bbox = request_body.bbox if request_body else None
    solutions = await get_filtered_solutions(db_session, targets, bbox)
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
