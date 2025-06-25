from typing import Literal, Union, Any, ForwardRef
from pydantic import BaseModel, ConfigDict, Field, model_validator


class GeometryBase(BaseModel):
    """Base class for all GeoJSON geometry types"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )


class PointGeometry(GeometryBase):
    """GeoJSON Point geometry"""

    type: Literal["Point"] = "Point"
    coordinates: list[float] = Field(..., min_length=2, max_length=3)

    @model_validator(mode="after")
    def validate_coordinates(self):
        """Validate Point coordinates: [longitude, latitude, (optional altitude)]"""
        lon, lat = self.coordinates[0], self.coordinates[1]
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return self


class LineStringGeometry(GeometryBase):
    """GeoJSON LineString geometry"""

    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]] = Field(..., min_length=2)

    @model_validator(mode="after")
    def validate_coordinates(self):
        """Validate LineString coordinates are valid points"""
        for point in self.coordinates:
            if len(point) < 2 or len(point) > 3:
                raise ValueError("Each point must have 2 or 3 coordinates")
            lon, lat = point[0], point[1]
            if not -180 <= lon <= 180:
                raise ValueError("Longitude must be between -180 and 180 degrees")
            if not -90 <= lat <= 90:
                raise ValueError("Latitude must be between -90 and 90 degrees")
        return self


class PolygonGeometry(GeometryBase):
    """GeoJSON Polygon geometry"""

    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]] = Field(...)

    @model_validator(mode="after")
    def validate_coordinates(self):
        """Validate Polygon rings are closed and valid"""
        for ring in self.coordinates:
            if len(ring) < 4:
                raise ValueError("A polygon ring must have at least 4 points")
            # Check if ring is closed
            if ring[0] != ring[-1]:
                raise ValueError(
                    "Polygon rings must be closed (first point equals last point)"
                )
            # Validate each point
            for point in ring:
                if len(point) < 2 or len(point) > 3:
                    raise ValueError("Each point must have 2 or 3 coordinates")
                lon, lat = point[0], point[1]
                if not -180 <= lon <= 180:
                    raise ValueError("Longitude must be between -180 and 180 degrees")
                if not -90 <= lat <= 90:
                    raise ValueError("Latitude must be between -90 and 90 degrees")
        return self


# Forward reference for GeoJSONGeometry type
GeoJSONGeometryRef = ForwardRef("GeoJSONGeometry")


class GeometryCollection(GeometryBase):
    """GeoJSON GeometryCollection"""

    type: Literal["GeometryCollection"] = "GeometryCollection"
    geometries: list[GeoJSONGeometryRef]


# Union type for all GeoJSON geometries
GeoJSONGeometry = Union[  # noqa: UP007
    PointGeometry, LineStringGeometry, PolygonGeometry, GeometryCollection
]


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature"""

    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONGeometry
    properties: dict[str, Any] | None = None
    id: str | int | None = None


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection"""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature]


# Resolve forward references
GeometryCollection.model_rebuild()
