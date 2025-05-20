from typing import Any
from geoalchemy2 import WKBElement
from shapely import from_wkb, to_wkb
from shapely.geometry import mapping, shape

from nbsapi.schemas.geometry import (
    PointGeometry,
    LineStringGeometry,
    PolygonGeometry,
    GeoJSONGeometry,
)


def wkb_to_geojson(wkb_element: WKBElement) -> dict[str, Any] | None:
    """Convert WKBElement to GeoJSON dict"""
    if wkb_element is None:
        return None

    # Convert from WKB to shapely geometry
    shape_geom = from_wkb(bytes(wkb_element.data))

    # Convert shapely geometry to GeoJSON dict
    return mapping(shape_geom)


def wkb_to_geometry_model(wkb_element: WKBElement) -> GeoJSONGeometry | None:
    """Convert WKBElement to appropriate Pydantic geometry model"""
    if wkb_element is None:
        return None

    geojson_dict = wkb_to_geojson(wkb_element)
    if geojson_dict is None:
        return None

    geom_type = geojson_dict["type"]

    if geom_type == "Point":
        return PointGeometry(**geojson_dict)
    elif geom_type == "LineString":
        return LineStringGeometry(**geojson_dict)
    elif geom_type == "Polygon":
        return PolygonGeometry(**geojson_dict)
    else:
        # Handle other geometry types as needed
        raise ValueError(f"Unsupported geometry type: {geom_type}")


def geometry_to_wkb(
    geometry: GeoJSONGeometry | dict[str, Any], srid: int = 4326
) -> WKBElement:
    """Convert GeoJSON geometry to WKBElement for database storage"""
    if isinstance(geometry, dict):
        geojson_dict = geometry
    else:
        geojson_dict = geometry.model_dump()

    # Convert GeoJSON dict to shapely geometry
    shapely_geom = shape(geojson_dict)

    # Convert shapely geometry to WKB
    wkb_data = to_wkb(shapely_geom)

    # Create WKBElement with SRID
    return WKBElement(wkb_data, srid=srid)


def calculate_area(geometry: GeoJSONGeometry | dict[str, Any]) -> float:
    """Calculate area of a geometry in square meters (assumes EPSG:4326)"""
    if isinstance(geometry, dict):
        geojson_dict = geometry
    else:
        geojson_dict = geometry.model_dump()

    # Convert GeoJSON dict to shapely geometry
    shapely_geom = shape(geojson_dict)

    # For polygons, calculate area in square meters
    # This is an approximation for geographic coordinates
    if shapely_geom.geom_type in {"Polygon", "MultiPolygon"}:
        # Calculate geodesic area (approximate for WGS84)
        return shapely_geom.area * (111320 * 111320)  # Convert degrees² to m²

    return 0.0  # Non-polygon geometries have zero area


def calculate_length(geometry: GeoJSONGeometry | dict[str, Any]) -> float:
    """Calculate length of a geometry in meters (assumes EPSG:4326)"""
    if isinstance(geometry, dict):
        geojson_dict = geometry
    else:
        geojson_dict = geometry.model_dump()

    # Convert GeoJSON dict to shapely geometry
    shapely_geom = shape(geojson_dict)

    # For linestrings, calculate length in meters
    # This is an approximation for geographic coordinates
    if shapely_geom.geom_type in {"LineString", "MultiLineString"}:
        # Calculate geodesic length (approximate for WGS84)
        return shapely_geom.length * 111320  # Convert degrees to meters

    return 0.0  # Non-linestring geometries have zero length
