# from nbsapi.api.dependencies.auth import validate_is_authenticated

from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Query

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


@router.post(
    "/solutions",
    response_model=List[NatureBasedSolutionRead],
)
async def get_solutions(
    db_session: DBSessionDep,
    targets: Optional[List[AdaptationTargetRead]] = Body(
        None, description="List of adaptation targets to filter by"
    ),
    bbox: Optional[List[float]] = Body(
        None,
        min_items=4,
        max_items=4,
        description="Bounding box specified as [west, south, east, north]. The list should contain exactly four float values. Max 1 sq km",
        examples=[
            [
                -6.2757665,
                53.332055,
                -6.274319,
                53.332553,
            ]
        ],
    ),
):
    """
    Return a list of nature-based solutions using _optional_ filter criteria:

    - `targets`: An array of one or more **adaptation targets** and their associated protection values. Solutions having targets with protection values **equal to or greater than** the specified values will be returned
    - `bbox`: An array of 4 EPSG 4326 coordinates: `[xmin, ymin, xmax, ymax]` / `[west, south, east, north]` Only solutions intersected by the bbox will be returned. It must be **<=** 1 km sq

    """
    # TODO: add optional bounding box and polygon params when we have PostGIS and geometry column
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
