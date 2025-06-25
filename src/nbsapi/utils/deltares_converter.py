"""Utilities for converting between API v2 and Deltares formats."""

import hashlib
from typing import Any
from nbsapi.schemas.project import ProjectRead
from nbsapi.schemas.naturebasedsolution import NatureBasedSolutionRead
from nbsapi.schemas.deltares import (
    DeltaresProjectExport,
    DeltaresFeature,
    DeltaresProperties,
    DeltaresApiData,
    DeltaresMapSettings,
    DeltaresSettings,
    DeltaresProjectArea,
    DeltaresTargets,
    DeltaresClimateTargets,
    DeltaresCostTargets,
    DeltaresWaterQualityTargets,
    DeltaresTargetValue,
)
from nbsapi.schemas.geometry import PointGeometry, LineStringGeometry, PolygonGeometry


def generate_feature_id(solution: NatureBasedSolutionRead) -> str:
    """Generate a unique feature ID for a solution."""
    # Use MD5 hash of the solution ID to create a consistent ID
    return hashlib.md5(str(solution.id).encode()).hexdigest()  # noqa: S324


def convert_geometry_to_dict(geometry: Any) -> dict[str, Any]:
    """Convert a pydantic geometry object to a dict for GeoJSON."""
    if isinstance(geometry, PointGeometry | LineStringGeometry | PolygonGeometry):
        return {"type": geometry.type, "coordinates": geometry.coordinates}
    elif hasattr(geometry, "model_dump"):
        return geometry.model_dump()
    return geometry


def convert_solution_to_deltares_feature(
    solution: NatureBasedSolutionRead,
) -> DeltaresFeature:
    """Convert a NatureBasedSolution to a Deltares Feature."""
    # Extract specialized impacts
    api_data = DeltaresApiData()

    # Process impacts
    for impact in solution.impacts:
        if hasattr(impact, "specialized") and impact.specialized:
            # Climate impacts
            if impact.specialized.climate:
                climate = impact.specialized.climate
                if climate.temp_reduction is not None:
                    api_data.tempReduction = climate.temp_reduction
                if climate.cool_spot is not None:
                    api_data.coolSpot = climate.cool_spot
                if climate.evapotranspiration is not None:
                    api_data.evapotranspiration = climate.evapotranspiration
                if climate.groundwater_recharge is not None:
                    api_data.groundwater_recharge = climate.groundwater_recharge
                if climate.storage_capacity is not None:
                    api_data.storageCapacity = climate.storage_capacity

            # Water quality impacts
            if impact.specialized.water_quality:
                water = impact.specialized.water_quality
                if water.capture_unit is not None:
                    api_data.captureUnit = water.capture_unit
                if water.filtering_unit is not None:
                    api_data.filteringUnit = water.filtering_unit
                if water.settling_unit is not None:
                    api_data.settlingUnit = water.settling_unit

            # Cost impacts
            if impact.specialized.cost:
                cost = impact.specialized.cost
                if cost.construction_cost is not None:
                    api_data.constructionCost = cost.construction_cost
                if cost.maintenance_cost is not None:
                    api_data.maintenanceCost = cost.maintenance_cost

    # Extract physical properties - could be dict or PhysicalProperties object
    physical = solution.physical_properties or {}
    if physical and hasattr(physical, "model_dump"):
        physical = physical.model_dump()

    # Extract styling data - could be dict or StylingProperties object
    styling_data = solution.styling
    if styling_data and hasattr(styling_data, "model_dump"):
        styling_data = styling_data.model_dump()

    # Build properties
    properties = DeltaresProperties(
        name=solution.name,
        hidden=styling_data.get("hidden", False) if styling_data else False,
        apiData=api_data,
        measure=solution.measure_id or "0",  # Default to "0" if no measure ID
        color=styling_data.get("color", "#3388ff") if styling_data else "#3388ff",
        defaultInflow=physical.get("default_inflow", 1.0),
        defaultDepth=physical.get("default_depth", 0.1),
        defaultWidth=physical.get("default_width", 1.0),
        defaultRadius=physical.get("default_radius", 1.0),
        areaInflow=physical.get("area_inflow"),
        areaDepth=str(physical.get("area_depth"))
        if physical.get("area_depth") is not None
        else None,
        areaWidth=physical.get("area_width"),
        areaRadius=physical.get("area_radius"),
        area=solution.area,
        length=solution.length,
    )

    # Convert geometry
    geometry_dict = (
        convert_geometry_to_dict(solution.geometry)
        if solution.geometry
        else {"type": "Point", "coordinates": [0, 0]}
    )

    return DeltaresFeature(
        id=generate_feature_id(solution),
        type="Feature",
        properties=properties,
        geometry=geometry_dict,
    )


def convert_project_targets(targets: dict[str, Any] | None) -> DeltaresTargets:
    """Convert project targets to Deltares format."""
    if not targets:
        return DeltaresTargets()

    deltares_targets = DeltaresTargets()

    # Climate targets
    if targets.get("climate"):
        climate_targets = DeltaresClimateTargets()
        climate = targets["climate"]

        if "temp_reduction" in climate:
            climate_targets.tempReduction = DeltaresTargetValue(
                **climate["temp_reduction"]
            )
        if "cool_spot" in climate:
            climate_targets.coolSpot = DeltaresTargetValue(**climate["cool_spot"])
        if "evapotranspiration" in climate:
            climate_targets.evapotranspiration = DeltaresTargetValue(
                **climate["evapotranspiration"]
            )
        if "groundwater_recharge" in climate:
            climate_targets.groundwater_recharge = DeltaresTargetValue(
                **climate["groundwater_recharge"]
            )
        if "storage_capacity" in climate:
            climate_targets.storageCapacity = DeltaresTargetValue(
                **climate["storage_capacity"]
            )

        deltares_targets.climate = climate_targets

    # Cost targets
    if targets.get("cost"):
        cost_targets = DeltaresCostTargets()
        cost = targets["cost"]

        if "construction_cost" in cost:
            cost_targets.constructionCost = DeltaresTargetValue(
                **cost["construction_cost"]
            )
        if "maintenance_cost" in cost:
            cost_targets.maintenanceCost = DeltaresTargetValue(
                **cost["maintenance_cost"]
            )

        deltares_targets.cost = cost_targets

    # Water quality targets
    if targets.get("water_quality"):
        water_targets = DeltaresWaterQualityTargets()
        water = targets["water_quality"]

        if "filtering_unit" in water:
            water_targets.filteringUnit = DeltaresTargetValue(**water["filtering_unit"])
        if "capture_unit" in water:
            water_targets.captureUnit = DeltaresTargetValue(**water["capture_unit"])
        if "settling_unit" in water:
            water_targets.settlingUnit = DeltaresTargetValue(**water["settling_unit"])

        deltares_targets.waterquality = water_targets

    return deltares_targets


def calculate_project_boundary(areas: list[DeltaresFeature]) -> dict[str, Any]:
    """Calculate a bounding polygon for all project areas."""
    if not areas:
        return {
            "type": "Feature",
            "properties": {"area": 0, "isProjectArea": True},
            "geometry": {"type": "Polygon", "coordinates": [[]]},
        }

    # Extract all coordinates from all geometries
    all_lons = []
    all_lats = []

    for area in areas:
        geom = area.geometry
        if geom["type"] == "Point":
            all_lons.append(geom["coordinates"][0])
            all_lats.append(geom["coordinates"][1])
        elif geom["type"] == "LineString":
            for coord in geom["coordinates"]:
                all_lons.append(coord[0])
                all_lats.append(coord[1])
        elif geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                for coord in ring:
                    all_lons.append(coord[0])
                    all_lats.append(coord[1])

    if not all_lons:
        return {
            "type": "Feature",
            "properties": {"area": 0, "isProjectArea": True},
            "geometry": {"type": "Polygon", "coordinates": [[]]},
        }

    # Create a bounding box with some padding
    min_lon = min(all_lons) - 0.001
    max_lon = max(all_lons) + 0.001
    min_lat = min(all_lats) - 0.001
    max_lat = max(all_lats) + 0.001

    # Create a polygon from the bounding box
    boundary_coords = [
        [min_lon, min_lat],
        [max_lon, min_lat],
        [max_lon, max_lat],
        [min_lon, max_lat],
        [min_lon, min_lat],
    ]

    # Calculate area using simple bounding box formula (approximate)
    width = max_lon - min_lon
    height = max_lat - min_lat
    boundary_area = width * height * (111320 * 111320)  # Convert degrees² to m²

    return {
        "type": "Feature",
        "properties": {"area": boundary_area, "isProjectArea": True},
        "geometry": {"type": "Polygon", "coordinates": [boundary_coords]},
    }


def convert_project_to_deltares(project: ProjectRead) -> DeltaresProjectExport:
    """Convert a Project to Deltares export format."""
    # Convert all solutions to Deltares features
    areas = [
        convert_solution_to_deltares_feature(solution) for solution in project.areas
    ]

    # Calculate map center from areas
    if areas:
        all_lons = []
        all_lats = []
        for area in areas:
            geom = area.geometry
            if geom["type"] == "Point":
                all_lons.append(geom["coordinates"][0])
                all_lats.append(geom["coordinates"][1])
            elif geom["type"] in ["LineString", "Polygon"]:
                coords = (
                    geom["coordinates"][0]
                    if geom["type"] == "Polygon"
                    else geom["coordinates"]
                )
                for coord in coords:
                    all_lons.append(coord[0])
                    all_lats.append(coord[1])

        center_lng = sum(all_lons) / len(all_lons)
        center_lat = sum(all_lats) / len(all_lats)
    else:
        center_lng = 0
        center_lat = 0

    # Build map settings
    map_settings = DeltaresMapSettings(
        center={"lat": center_lat, "lng": center_lng},
        zoom=project.map.zoom if project.map and project.map.zoom else 16,
    )

    # Build project area settings
    project_area = DeltaresProjectArea(
        scenarioName=project.settings.scenario_name
        if project.settings and project.settings.scenario_name
        else "Default Scenario",
        capacity=project.settings.capacity
        if project.settings and project.settings.capacity
        else {
            "heatCoping": False,
            "droughtCoping": False,
            "floodCoping": False,
            "waterSafetyCoping": False,
        },
        multifunctionality=project.settings.multifunctionality
        if project.settings and project.settings.multifunctionality
        else "1",
        scale=project.settings.scale
        if project.settings and project.settings.scale
        else {"city": False, "neighbourhood": True, "street": False, "building": False},
        suitability=project.settings.suitability
        if project.settings and project.settings.suitability
        else {
            "greySpace": True,
            "greenSpacePrivateGardens": False,
            "greenSpaceNoRecreation": False,
            "greenSpaceRecreationUrbanFarming": False,
            "greyGreenSpaceSportsPlayground": False,
            "redSpace": False,
            "blueSpace": False,
        },
        subsurface=project.settings.subsurface
        if project.settings and project.settings.subsurface
        else "medium",
        surface=project.settings.surface
        if project.settings and project.settings.surface
        else "mixed",
        soil=project.settings.soil
        if project.settings and project.settings.soil
        else "clay",
        slope=project.settings.slope
        if project.settings and project.settings.slope
        else "flat",
    )

    # Build settings
    settings = DeltaresSettings(
        area=calculate_project_boundary(areas),
        general={"title": project.title},
        projectArea=project_area,
        targets=convert_project_targets(
            project.targets.model_dump() if project.targets else None
        ),
    )

    # Build measure overrides from unique measure types in the project
    measure_overrides = {}
    for area in areas:
        measure_id = area.properties.measure
        if measure_id not in measure_overrides:
            measure_overrides[measure_id] = {"color": {"hex": area.properties.color}}

    return DeltaresProjectExport(
        areas=areas,
        legalAccepted=True,
        map=map_settings,
        displayMap=True,
        settings=settings,
        measureOverrides=measure_overrides,
        savedInWorkspace=None,
    )
