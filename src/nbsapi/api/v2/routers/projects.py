from fastapi import APIRouter, Depends, Path, Query, HTTPException

from nbsapi.api.dependencies.auth import validate_is_authenticated
from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.crud.project import (
    get_project,
    get_all_projects,
    create_project,
    update_project,
    delete_project,
    add_solution_to_project,
    remove_solution_from_project,
)
from nbsapi.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from nbsapi.schemas.deltares import DeltaresProjectExport
from nbsapi.utils.deltares_converter import convert_project_to_deltares

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)


@router.get(
    "",
    response_model=list[ProjectRead],
    response_model_exclude_none=True,
    summary="Get all projects",
    description="Retrieves a list of all available projects with their associated nature-based solutions",
)
async def read_projects(db_session: DBSessionDep):
    """
    Retrieve all projects

    This endpoint returns a list of all projects in the system. Each project includes:
    - Basic metadata (title, description)
    - Project settings (scenario, capacity, etc.)
    - Map settings for visualization
    - Targets for different metrics
    - All nature-based solutions associated with the project

    Projects are a new concept in v2 that allow organizing multiple NBS solutions
    with common settings and targets.
    """
    projects = await get_all_projects(db_session)
    return projects


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    response_model_exclude_none=True,
    summary="Get a project",
    description="Retrieves a specific project by its ID with all associated solutions and settings",
)
async def read_project(
    db_session: DBSessionDep,
    project_id: str = Path(..., description="The ID of the project"),
):
    """
    Retrieve a specific project by ID

    This endpoint returns detailed information about a specific project, including:
    - Basic metadata (title, description)
    - Project settings (scenario, capacity, etc.)
    - Map settings for visualization
    - Targets for different metrics
    - All nature-based solutions associated with the project

    Each project can contain multiple nature-based solutions, allowing for
    organizing solutions that work together to address specific challenges.
    """
    project = await get_project(db_session, project_id)
    return project


@router.post(
    "",
    response_model=ProjectRead,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Create a project",
    description="Creates a new project with optional settings, targets, and associated nature-based solutions",
    status_code=200,
    responses={
        200: {
            "description": "Project created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "proj-deltares-001",
                        "title": "Votris project area",
                        "description": "Urban nature-based solutions implementation",
                        "settings": {
                            "scenario_name": "Athens_area_5_Medium_density_mixed_use",
                            "capacity": {
                                "heatCoping": True,
                                "droughtCoping": True,
                                "floodCoping": True,
                                "waterSafetyCoping": False,
                            },
                            "multifunctionality": "1",
                            "scale": {
                                "city": False,
                                "neighbourhood": True,
                                "street": True,
                                "building": True,
                            },
                            "suitability": {
                                "greySpace": True,
                                "greenSpacePrivateGardens": True,
                                "greenSpaceNoRecreation": True,
                                "greenSpaceRecreationUrbanFarming": False,
                                "greyGreenSpaceSportsPlayground": True,
                                "redSpace": True,
                                "blueSpace": False,
                            },
                            "subsurface": "high",
                            "surface": "flatRoofs",
                            "soil": "sand",
                            "slope": "flatAreaHighGround",
                        },
                        "map": {
                            "center": [23.71841890133385, 38.00910725441946],
                            "zoom": 16,
                            "base_layer": "OpenStreetMap",
                        },
                        "targets": {
                            "climate": {
                                "storage_capacity": {"include": True, "value": "1400"},
                                "temp_reduction": {"include": True, "value": "0"},
                            },
                            "water_quality": {
                                "filtering_unit": {"include": True, "value": "100"}
                            },
                        },
                        "areas": [],
                    }
                }
            },
        },
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        404: {"description": "One or more solutions not found"},
    },
)
async def create_new_project(
    project_data: ProjectCreate,
    db_session: DBSessionDep,
    project_id: str | None = Query(
        None, description="Override project ID (for testing/import purposes)"
    ),
):
    """
    Create a new project

    This endpoint creates a new project with the provided data.
    You can optionally include existing nature-based solutions by providing their IDs.

    Projects are designed to organize multiple NBS solutions with shared settings,
    targets, and spatial contexts. They are particularly useful for:
    - Deltares project imports
    - Scenario planning
    - Performance target management
    - Collaborative project development

    ## HTTP Request Example:
    ```http
    POST /v2/api/projects HTTP/1.1
    Host: your-api-host.com
    Content-Type: application/json
    Authorization: Bearer your-access-token

    {
      "title": "Votris project area",
      "description": "Urban nature-based solutions implementation",
      "settings": {
        "scenario_name": "Athens_area_5_Medium_density_mixed_use",
        "capacity": {
          "heatCoping": true,
          "droughtCoping": true,
          "floodCoping": true,
          "waterSafetyCoping": false
        },
        "multifunctionality": "1",
        "scale": {
          "city": false,
          "neighbourhood": true,
          "street": true,
          "building": true
        },
        "suitability": {
          "greySpace": true,
          "greenSpacePrivateGardens": true,
          "greenSpaceNoRecreation": true,
          "greenSpaceRecreationUrbanFarming": false,
          "greyGreenSpaceSportsPlayground": true,
          "redSpace": true,
          "blueSpace": false
        },
        "subsurface": "high",
        "surface": "flatRoofs",
        "soil": "sand",
        "slope": "flatAreaHighGround"
      },
      "map": {
        "center": [23.71841890133385, 38.00910725441946],
        "zoom": 16,
        "base_layer": "OpenStreetMap"
      },
      "targets": {
        "climate": {
          "storage_capacity": {
            "include": true,
            "value": "1400"
          },
          "groundwater_recharge": {
            "include": true,
            "value": "0"
          },
          "temp_reduction": {
            "include": true,
            "value": "0"
          }
        },
        "cost": {
          "construction_cost": {
            "include": true,
            "value": "0"
          }
        },
        "water_quality": {
          "filtering_unit": {
            "include": true,
            "value": "100"
          },
          "capture_unit": {
            "include": true,
            "value": "100"
          }
        }
      },
      "areas": [1, 2, 3]
    }
    ```

    ## Project Components:

    ### Settings
    - `scenario_name`: Descriptive name for the scenario
    - `capacity`: Coping mechanisms (heat, drought, flood, water safety)
    - `multifunctionality`: Multifunctionality level
    - `scale`: Applicable scales (city, neighbourhood, street, building)
    - `suitability`: Space type suitability settings
    - Physical site characteristics: `subsurface`, `surface`, `soil`, `slope`

    ### Map Settings
    - `center`: Map center coordinates [longitude, latitude]
    - `zoom`: Zoom level for initial view
    - `base_layer`: Base map layer type

    ### Targets
    Project-level targets define performance goals across all solutions in the project.
    Unlike v1 adaptation targets (solution-specific qualitative scores),
    v2 targets are quantitative and project-wide:

    #### Climate Targets
    - `storage_capacity`: Total water storage goal (m³)
    - `groundwater_recharge`: Recharge rate target (mm/day)
    - `evapotranspiration`: Evapotranspiration target (mm/day)
    - `temp_reduction`: Temperature reduction goal (°C)
    - `cool_spot`: Number of cool spots to create

    #### Cost Targets
    - `construction_cost`: Maximum construction budget
    - `maintenance_cost`: Annual maintenance budget limit

    #### Water Quality Targets
    - `filtering_unit`: Filtration capacity target
    - `capture_unit`: Pollutant capture goal
    - `settling_unit`: Sedimentation efficiency target

    Each target includes:
    - `include`: Whether to include in calculations
    - `value`: Target value (supports formulas like "area * 0.2")

    ### Architecture Differences
    - **Project-wide goals** instead of solution-specific adaptations
    - **Quantitative targets** instead of qualitative scores
    - **Formula support** for dynamic calculations
    - **Deltares compatibility** for project imports

    Authentication is required for this endpoint.

    ### Query Parameters
    - `project_id`: Optional. Override the generated project ID. Useful for testing
      and import purposes where a specific ID is required.
    """
    project = await create_project(db_session, project_data, project_id)
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Update a project",
    description="Updates specific fields of an existing project while keeping other fields unchanged",
)
async def update_existing_project(
    project_data: ProjectUpdate,
    db_session: DBSessionDep,
    project_id: str = Path(..., description="The ID of the project"),
):
    """
    Update an existing project

    This endpoint updates an existing project with the provided data.
    Only the fields that are provided will be updated. This allows for
    partial updates without needing to provide the complete project data.

    Fields that can be updated include:
    - Basic metadata (title, description)
    - Project settings (scenario, capacity, etc.)
    - Map settings (center, zoom level, etc.)
    - Targets (climate, water quality, costs)
    - Associated solutions

    Authentication is required for this endpoint.

    Example partial update (changing only the title and adding new solutions):
    ```json
    {
      "title": "Updated Project Title",
      "areas": [1, 2, 3, 4, 5]
    }
    ```
    """
    project = await update_project(db_session, project_id, project_data)
    return project


@router.delete(
    "/{project_id}",
    response_model=dict,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Delete a project",
    description="Permanently deletes a project (this operation cannot be undone)",
    responses={
        200: {"description": "Project deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Project not found"},
    },
)
async def delete_existing_project(
    db_session: DBSessionDep,
    project_id: str = Path(..., description="The ID of the project"),
):
    """
    Delete a project

    This endpoint permanently deletes a project and removes its association with
    nature-based solutions. The associated solutions themselves are not deleted.

    Authentication is required for this endpoint.

    ⚠️ **Warning**: This operation cannot be undone. The project and all its
    settings, targets, and associations will be permanently removed.
    """
    await delete_project(db_session, project_id)
    return {"message": f"Project {project_id} deleted successfully"}


@router.post(
    "/{project_id}/solutions/{solution_id}",
    response_model=ProjectRead,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Add solution to project",
    description="Adds an existing nature-based solution to a project",
    responses={
        200: {"description": "Solution added to project successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Project or solution not found"},
        409: {"description": "Solution already in project"},
    },
)
async def add_solution_to_existing_project(
    db_session: DBSessionDep,
    project_id: str = Path(..., description="The ID of the project"),
    solution_id: int = Path(..., description="The ID of the nature-based solution"),
):
    """
    Add a nature-based solution to a project

    This endpoint adds an existing nature-based solution to a project. This
    establishes an association between the project and the solution, allowing
    the solution to be included in project-level calculations and visualizations.

    A solution can be part of multiple projects, and a project can contain
    multiple solutions.

    Authentication is required for this endpoint.
    """
    project = await add_solution_to_project(db_session, project_id, solution_id)
    return project


@router.delete(
    "/{project_id}/solutions/{solution_id}",
    response_model=ProjectRead,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Remove solution from project",
    description="Removes a nature-based solution from a project",
    responses={
        200: {"description": "Solution removed from project successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Project or solution not found"},
        409: {"description": "Solution not in project"},
    },
)
async def remove_solution_from_existing_project(
    db_session: DBSessionDep,
    project_id: str = Path(..., description="The ID of the project"),
    solution_id: int = Path(..., description="The ID of the nature-based solution"),
):
    """
    Remove a nature-based solution from a project

    This endpoint removes a nature-based solution from a project. This breaks
    the association between the project and the solution, but does not delete
    the solution itself.

    Authentication is required for this endpoint.
    """
    project = await remove_solution_from_project(db_session, project_id, solution_id)
    return project


@router.post(
    "/import",
    response_model=ProjectRead,
    response_model_exclude_none=True,
    dependencies=[Depends(validate_is_authenticated)],
    summary="Import a project",
    description="Imports a complete project from an external source",
    status_code=200,
    responses={
        200: {"description": "Project imported successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        409: {"description": "Project ID already exists"},
    },
)
async def import_project(
    project_data: ProjectRead,
    db_session: DBSessionDep,
):
    """
    Import a project

    This endpoint imports a complete project from an external source. The
    project data must include all required fields and can include optional
    fields like settings, targets, and associated solutions.

    This is useful for transferring projects between systems or restoring
    projects from backups.

    Authentication is required for this endpoint.

    Example input is a complete ProjectRead object including an ID:
    ```json
    {
      "id": "proj-imported123",
      "title": "Imported Project",
      "description": "A project imported from another system",
      "settings": { ... },
      "targets": { ... },
      "areas": [ ... ]
    }
    ```
    """
    # Verify that the project ID doesn't already exist
    try:
        await get_project(db_session, project_data.id)
        raise HTTPException(  # noqa: TRY301
            status_code=409, detail=f"Project with ID {project_data.id} already exists"
        )
    except HTTPException as e:
        if e.status_code != 404:
            raise

    # Create a ProjectCreate object from the ProjectRead
    project_create = ProjectCreate(
        title=project_data.title,
        description=project_data.description,
        settings=project_data.settings,
        map=project_data.map,
        targets=project_data.targets,
        areas=[area.id for area in project_data.areas],
    )

    # Use the create_project function but override the ID
    project = await create_project(db_session, project_create)
    return project


@router.get(
    "/{project_id}/export",
    response_model=ProjectRead,
    response_model_exclude_none=True,
    summary="Export a project",
    description="Exports a project in a format suitable for transfer to other systems",
)
async def export_project(
    db_session: DBSessionDep,
    project_id: str = Path(..., description="The ID of the project"),
):
    """
    Export a project

    This endpoint exports a project to an external format that can be imported
    into another system or saved as a backup. The exported project includes all
    project data:

    - Project ID and metadata (title, description)
    - Project settings (scenario, capacity, etc.)
    - Map settings (center, zoom level, etc.)
    - Targets for different metrics
    - All associated nature-based solutions with their complete data

    The exported format is identical to the one used by the import endpoint,
    allowing for seamless transfer between systems.
    """
    project = await get_project(db_session, project_id)
    return project


@router.get(
    "/{project_id}/export/deltares",
    response_model=DeltaresProjectExport,
    response_model_exclude_none=True,
    summary="Export a project in Deltares format",
    description="Exports a project in Deltares-compatible GeoJSON format",
)
async def export_project_deltares(
    db_session: DBSessionDep,
    project_id: str = Path(..., description="The ID of the project"),
):
    """
    Export a project in Deltares format

    This endpoint exports a project in a format compatible with the Deltares API.
    The export includes:

    - All NBS areas as GeoJSON Features with Deltares-specific properties
    - Project settings in Deltares format (scenarioName, capacity, etc.)
    - Project targets with Deltares field names (camelCase)
    - Map configuration and display settings
    - Measure type overrides for colors

    The exported format uses camelCase field names for compatibility with Deltares
    systems and includes all specialized impact data (climate, water quality, costs)
    in a flattened `apiData` structure.

    This format is particularly useful for:
    - Integration with Deltares climate adaptation tools
    - Visualization in Deltares-compatible mapping applications
    - Data exchange with other systems using the Deltares API standard
    """
    project = await get_project(db_session, project_id)
    return convert_project_to_deltares(project)
