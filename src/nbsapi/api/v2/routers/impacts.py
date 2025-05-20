from fastapi import APIRouter, Depends, HTTPException, Path

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.enhanced_impact import (
    create_enhanced_impact,
    get_enhanced_impact,
    get_enhanced_impacts_for_solution,
)
from nbsapi.crud.impact import (
    get_impact_intensities,
    get_impact_units,
    create_impact_intensity,
    create_impact_unit,
)
from nbsapi.schemas.impact import ImpactIntensity, ImpactUnit
from nbsapi.schemas.specialized_impacts import EnhancedImpactBase

router = APIRouter(
    prefix="/api/impacts",
    tags=["impacts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/intensities", response_model=list[ImpactIntensity])
async def read_impact_intensities(db_session: DBSessionDep):
    """Retrieve all available impact intensities"""
    intensities = await get_impact_intensities(db_session)
    return intensities


@router.get("/units", response_model=list[ImpactUnit])
async def read_impact_units(db_session: DBSessionDep):
    """Retrieve all available impact units"""
    units = await get_impact_units(db_session)
    return units


@router.post(
    "/intensities",
    response_model=ImpactIntensity,
    dependencies=[Depends(validate_is_authenticated)],
)
async def write_impact_intensity(intensity: ImpactIntensity, db_session: DBSessionDep):
    """Create a new impact intensity"""
    intensity = await create_impact_intensity(db_session, intensity)
    return intensity


@router.post(
    "/units",
    response_model=ImpactUnit,
    dependencies=[Depends(validate_is_authenticated)],
)
async def write_impact_unit(unit: ImpactUnit, db_session: DBSessionDep):
    """Create a new impact unit"""
    unit = await create_impact_unit(db_session, unit)
    return unit


# V2 Enhanced impacts with specialized data
@router.get(
    "/solutions/{solution_id}/impacts",
    response_model=list[EnhancedImpactBase],
    response_model_exclude_none=True,
    summary="Get solution impacts",
    description="Retrieve all quantitative impacts for a solution, including specialized climate, water quality, and cost data",
)
async def read_solution_impacts(
    db_session: DBSessionDep,
    solution_id: int = Path(..., description="The ID of the solution"),
):
    """
    Retrieve all impacts for a solution, including specialized impact data.

    ## Specialized Impact Categories

    v2 uses quantitative specialized impacts instead of abstract adaptation targets:

    - **Climate Impacts**: Environmental effects
      - Temperature reduction (°C)
      - Water storage capacity (m³)
      - Evapotranspiration rates (mm/day)
      - Groundwater recharge (mm/day)
      - Cool spot indicators

    - **Water Quality Impacts**: Water treatment effects
      - Pollutant capture efficiency
      - Filtration capacity
      - Sedimentation rates

    - **Cost Impacts**: Economic data
      - Construction costs with currency
      - Annual maintenance costs

    ## Migration from v1
    - **v1**: `"adaptations": [{"type": "Heat", "value": 80}]`
    - **v2**: `{"specialized": {"climate": {"temp_reduction": 1.5}}}`

    Returns all impacts associated with a solution for performance analysis.
    """
    impacts = await get_enhanced_impacts_for_solution(db_session, solution_id)
    return impacts


@router.get(
    "/impacts/{impact_id}",
    response_model=EnhancedImpactBase,
    response_model_exclude_none=True,
)
async def read_impact(
    db_session: DBSessionDep,
    impact_id: int = Path(..., description="The ID of the impact"),
):
    """
    Retrieve a specific impact with specialized data
    """
    impact = await get_enhanced_impact(db_session, impact_id)
    if not impact:
        raise HTTPException(status_code=404, detail="Impact not found")
    return impact


@router.post(
    "/solutions/{solution_id}/impacts",
    response_model=EnhancedImpactBase,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    responses={
        200: {
            "description": "Impact created successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "climate_impact": {
                            "summary": "Climate impact with storage capacity",
                            "value": {
                                "magnitude": 142.33955129172907,
                                "unit": {
                                    "unit": "m3",
                                    "description": "storage capacity",
                                },
                                "intensity": {"intensity": "high"},
                                "specialized": {
                                    "climate": {
                                        "temp_reduction": 0.05763750310256802,
                                        "cool_spot": 0,
                                        "evapotranspiration": 0.04105408115726775,
                                        "groundwater_recharge": -0.04348092339316535,
                                        "storage_capacity": 142.33955129172907,
                                    }
                                },
                            },
                        },
                        "water_quality_impact": {
                            "summary": "Water quality improvement impact",
                            "value": {
                                "magnitude": 1.8201316769232005,
                                "unit": {
                                    "unit": "units",
                                    "description": "water quality improvement",
                                },
                                "intensity": {"intensity": "medium"},
                                "specialized": {
                                    "water_quality": {
                                        "capture_unit": -0.2831315941880535,
                                        "filtering_unit": 1.8201316769232005,
                                        "settling_unit": 1.8403553622223476,
                                    }
                                },
                            },
                        },
                        "cost_impact": {
                            "summary": "Construction cost impact",
                            "value": {
                                "magnitude": 58381.40474038341,
                                "unit": {
                                    "unit": "EUR",
                                    "description": "construction cost",
                                },
                                "intensity": {"intensity": "high"},
                                "specialized": {
                                    "cost": {
                                        "construction_cost": 58381.40474038341,
                                        "maintenance_cost": 245.20189990961032,
                                        "currency": "EUR",
                                    }
                                },
                            },
                        },
                    }
                }
            },
        }
    },
)
async def create_solution_impact(
    impact: EnhancedImpactBase,
    db_session: DBSessionDep,
    solution_id: int = Path(..., description="The ID of the solution"),
):
    """
    Create a new impact for a solution with optional specialized data.

    ## Specialized Impact Types:

    ### Climate Impacts
    - `temp_reduction`: Temperature reduction in degrees Celsius
    - `cool_spot`: Cool spot metric (0 or 1)
    - `evapotranspiration`: Evapotranspiration in mm/day
    - `groundwater_recharge`: Groundwater recharge in mm/day (negative values indicate loss)
    - `storage_capacity`: Water storage capacity in cubic meters

    ### Water Quality Impacts
    - `capture_unit`: Pollutant capture efficiency
    - `filtering_unit`: Filtration efficiency
    - `settling_unit`: Sedimentation efficiency

    ### Cost Impacts
    - `construction_cost`: Construction cost in currency units
    - `maintenance_cost`: Annual maintenance cost
    - `currency`: Currency code (EUR, USD, etc.)

    ## HTTP Request Example:
    ```http
    POST /v2/api/impacts/solutions/1/impacts HTTP/1.1
    Host: your-api-host.com
    Content-Type: application/json
    Authorization: Bearer your-access-token

    {
      "magnitude": 142.33955129172907,
      "unit": {
        "unit": "m3",
        "description": "storage capacity"
      },
      "intensity": {
        "intensity": "high"
      },
      "specialized": {
        "climate": {
          "temp_reduction": 0.05763750310256802,
          "cool_spot": 0,
          "evapotranspiration": 0.04105408115726775,
          "groundwater_recharge": -0.04348092339316535,
          "storage_capacity": 142.33955129172907
        }
      }
    }
    ```

    Authentication is required for this endpoint.
    """
    db_impact = await create_enhanced_impact(db_session, solution_id, impact)

    # Store the ID before committing (after flush in create_enhanced_impact)
    impact_id = db_impact.id
    await db_session.commit()

    # Return the created impact
    return await get_enhanced_impact(db_session, impact_id)
