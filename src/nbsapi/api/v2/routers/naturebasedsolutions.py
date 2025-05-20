from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.naturebasedsolution import (
    create_nature_based_solution,
    get_filtered_solutions,
    get_solution,
    update_nature_based_solution as crud_update_nature_based_solution,
)

# AdaptationTargets are deprecated in v2 - use specialized impacts instead
from nbsapi.schemas.geometry import GeoJSONFeature, GeoJSONFeatureCollection
from nbsapi.schemas.impact import ImpactIntensity
from nbsapi.schemas.naturebasedsolution import (
    NatureBasedSolutionCreate,
    NatureBasedSolutionRead,
    NatureBasedSolutionUpdate,
)

router = APIRouter(
    prefix="/api/solutions",
    tags=["solutions"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)


# Define v2 request and response models that include GeoJSON support
class SolutionRequestV2(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "bbox": [-6.2757665, 53.332055, -6.274319, 53.332553],
                    "adaptation": {"type": "Heat", "value": 10},
                    "intensities": [{"intensity": "low"}],
                }
            ]
        }
    )
    # Note: targets parameter is deprecated in v2 - use specialized impacts instead
    targets: list | None = Body(
        None,
        description="[DEPRECATED] List of adaptation targets to filter by. Use specialized impacts instead.",
        deprecated=True,
    )
    intensities: list[ImpactIntensity] | None = Body(
        None, description="List of impact intensities to filter by"
    )
    bbox: list[float] | None = Field(
        None,
        description="Bounding box specified as [west, south, east, north]. The list should contain exactly four float values. Max 1 sq km",
        min_length=4,
        max_length=4,
    )

    @model_validator(mode="before")
    @classmethod
    def check_bbox(cls, values):
        if isinstance(values, dict):
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


class NatureBasedSolutionFeature(GeoJSONFeature):
    """GeoJSON Feature with NatureBasedSolution properties"""

    properties: NatureBasedSolutionRead


class NatureBasedSolutionCollection(GeoJSONFeatureCollection):
    """GeoJSON FeatureCollection with NatureBasedSolution features"""

    features: list[NatureBasedSolutionFeature]


# V2 Routes with GeoJSON support
@router.get(
    "/solutions/{solution_id}",
    response_model=NatureBasedSolutionRead,
    response_model_exclude_none=True,
    summary="Get a nature-based solution",
    description="Retrieves a specific nature-based solution by its ID with full details including geometry, styling, and physical properties",
)
async def read_nature_based_solution(solution_id: int, db_session: DBSessionDep):
    """Retrieve a nature-based solution using its ID

    This endpoint returns the complete details of a specific nature-based solution including:
    - Basic metadata (name, definition, etc.)
    - Geometry (GeoJSON format if available)
    - Styling properties
    - Physical properties
    - Adaptation targets
    - Impacts

    The response includes all fields from the v1 API with additional v2 fields for enhanced functionality.
    """
    solution = await get_solution(db_session, solution_id)
    return solution


@router.get(
    "/solutions/{solution_id}/geojson",
    response_model=NatureBasedSolutionFeature,
    response_model_exclude_none=True,
    summary="Get a nature-based solution as GeoJSON Feature",
    description="Returns a GeoJSON Feature representation of a specific solution, with the solution properties included",
)
async def read_nature_based_solution_as_geojson(
    solution_id: int, db_session: DBSessionDep
):
    """Retrieve a nature-based solution as a GeoJSON Feature

    This endpoint returns a standard GeoJSON Feature object where:
    - `geometry` contains the solution's GeoJSON geometry (Point, LineString, or Polygon)
    - `properties` contains the full solution details
    - `id` contains the solution's ID

    This format is ideal for direct integration with mapping libraries that support GeoJSON.
    """
    solution = await get_solution(db_session, solution_id)

    # Create a GeoJSON Feature from the solution
    feature = NatureBasedSolutionFeature(
        type="Feature", geometry=solution.geometry, properties=solution, id=solution.id
    )

    return feature


@router.post(
    "/solutions",
    response_model=list[NatureBasedSolutionRead],
    response_model_exclude_none=True,
    summary="Find nature-based solutions",
    description="Search for nature-based solutions using filter criteria like spatial bounds, adaptation targets, and impact intensities",
)
async def get_solutions(
    db_session: DBSessionDep,
    request_body: SolutionRequestV2 | None = Body(None),
    as_geojson: bool = Query(
        False, description="Return results as GeoJSON FeatureCollection"
    ),
):
    """
    Return a list of nature-based solutions using _optional_ filter criteria:

    - `targets`: An array of one or more **adaptation targets** and their associated protection values. Solutions having targets with protection values **equal to or greater than** the specified values will be returned
    - `bbox`: An array of 4 EPSG 4326 coordinates: `[xmin, ymin, xmax, ymax]` / `[west, south, east, north]` Only solutions intersected by the bbox will be returned. It must be **<=** 1 km sq
    - `intensity`: An array of one or more **adaptation intensities**
    - `as_geojson`: Set to true to return results as a GeoJSON FeatureCollection

    When `as_geojson` is true, the response will be a GeoJSON FeatureCollection where each feature represents a solution.
    This makes it ideal for direct display on interactive maps.

    The response includes the enhanced v2 fields like geometry, styling, and physical properties.
    """
    targets = request_body.targets if request_body else None
    bbox = request_body.bbox if request_body else None
    intensities = request_body.intensities if request_body else None

    solutions = await get_filtered_solutions(db_session, targets, bbox, intensities)

    if as_geojson:
        # Convert to GeoJSON
        features = [
            NatureBasedSolutionFeature(
                type="Feature",
                geometry=solution.geometry,
                properties=solution,
                id=solution.id,
            )
            for solution in solutions
            if solution.geometry is not None
        ]

        return NatureBasedSolutionCollection(
            type="FeatureCollection", features=features
        )
    else:
        return solutions


@router.post(
    "/add_solution",
    response_model=NatureBasedSolutionRead,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Create a new nature-based solution",
    description="Create a new nature-based solution with enhanced v2 features like GeoJSON geometry, styling, and physical properties",
    status_code=200,
    responses={
        200: {
            "description": "Solution created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Area-1",
                        "definition": "Imported from Deltares format",
                        "cobenefits": "Various environmental benefits",
                        "specificdetails": "Details from Deltares import",
                        "location": "Imported location",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        [23.717992514920383, 38.00993916350677],
                                        [23.71835238960557, 38.00987732368668],
                                        [23.718232201749544, 38.009469169435704],
                                        [23.718133541363812, 38.00911729628717],
                                        [23.717763276983078, 38.009161267544044],
                                        [23.717992514920383, 38.00993916350677],
                                    ]
                                ]
                            ],
                        },
                        "styling": {"color": "#cfdd20", "hidden": False},
                        "physical_properties": {
                            "default_inflow": 1,
                            "default_depth": 0.05,
                            "default_width": 5,
                            "default_radius": 1,
                            "area_depth": 0.05,
                        },
                        "area": 3672.3235347681,
                        "measure_id": "39",
                        "impacts": [],
                        "solution_targets": [],
                    }
                }
            },
        },
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        409: {"description": "Solution already exists"},
    },
)
async def write_nature_based_solution(
    solution: NatureBasedSolutionCreate, db_session: DBSessionDep
):
    """
    Add a nature-based solution with optional GeoJSON geometry.

    The payload must be a `NatureBasedSolutionCreate` object that includes:
    - Required basic fields (name, definition, etc.)
    - Optional GeoJSON geometry (Point, LineString, or Polygon)
    - Optional styling properties for visual representation
    - Optional physical properties for dimensions
    - Optional measure_id referencing predefined measure types
    - Optional impacts (basic or specialized)
    - Optional adaptation targets

    Authentication is required for this endpoint.

    ## HTTP Request Example:
    ```http
    POST /v2/api/solutions/add_solution HTTP/1.1
    Host: your-api-host.com
    Content-Type: application/json
    Authorization: Bearer your-access-token

    {
      "name": "Area-1",
      "definition": "Imported from Deltares format",
      "cobenefits": "Various environmental benefits",
      "specificdetails": "Details from Deltares import",
      "location": "Imported location",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [23.717992514920383, 38.00993916350677],
          [23.71835238960557, 38.00987732368668],
          [23.718232201749544, 38.009469169435704],
          [23.718133541363812, 38.00911729628717],
          [23.717763276983078, 38.009161267544044],
          [23.717992514920383, 38.00993916350677]
        ]]
      },
      "styling": {
        "color": "#cfdd20",
        "hidden": false
      },
      "physical_properties": {
        "default_inflow": 1,
        "default_depth": 0.05,
        "default_width": 5,
        "default_radius": 1,
        "area_depth": 0.05
      },
      "measure_id": "39",
      "area": 3672.3235347681,
      "impacts": [
        {
          "magnitude": 10.0,
          "unit": {
            "unit": "m2",
            "description": "area"
          },
          "intensity": {
            "intensity": "medium"
          }
        }
      ],
      "adaptations": []
    }
    ```

    ## Geometry Types:
    - **Polygon**: For area-based solutions (rain gardens, wetlands)
    - **LineString**: For linear solutions (bioswales, green corridors)
    - **Point**: For point-based solutions (infiltration wells, trees)

    ## Measure Types:
    Common measure IDs from Deltares:
    - `6`: Bioswale
    - `8`: Detention pond
    - `12`: Green roof
    - `15`: Permeable pavement
    - `25`: Urban forest
    - `26`: Wetland
    - `33`: Underground storage
    - `37`: Infiltration well
    - `39`: Rain garden
    - `40`: Retention pond
    - `41`: Large detention basin
    - `45`: Green corridor
    """
    solution = await create_nature_based_solution(db_session, solution)
    return solution


@router.patch(
    "/solutions/{solution_id}",
    response_model=NatureBasedSolutionRead,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Update a nature-based solution",
    description="Update specific fields of an existing nature-based solution while keeping other fields unchanged",
)
async def update_nature_based_solution(
    solution_id: int,
    update_data: NatureBasedSolutionUpdate,
    db_session: DBSessionDep,
):
    """
    Update an existing nature-based solution.

    Only the provided fields will be updated. Other fields will remain unchanged.
    This allows for partial updates of solution properties without needing to provide
    the complete solution data.

    Fields that can be updated include:
    - Basic metadata (name, definition, etc.)
    - GeoJSON geometry
    - Styling properties
    - Physical properties
    - Adaptation targets

    Authentication is required for this endpoint.

    Example partial update (changing only geometry):
    ```json
    {
      "geometry": {
        "type": "Point",
        "coordinates": [4.901, 52.369]
      }
    }
    ```
    """
    updated_solution = await crud_update_nature_based_solution(
        db_session, solution_id, update_data
    )
    return updated_solution
