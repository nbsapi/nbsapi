# NBSAPI v2 Documentation

This document provides an overview of the NBSAPI v2, an API for interoperability between digital tools that help build and manage nature-based solutions (NbS) in the built and natural environment.

## Overview

The NBSAPI v2 extends the core concepts of v1 with richer data models, GeoJSON support, and project-level organization. It's designed to support complex NbS tools and integrations with specialized environmental metrics.

## Key Features of v2

- **Full GeoJSON Support**: Define the geometry of solutions using GeoJSON
- **Specialized Impact Metrics**: Detailed impact measurements for climate, water quality, and costs
- **Physical Properties**: Define physical dimensions of solutions
- **Project Management**: Group solutions into projects with targets and settings
- **Deltares Compatibility**: Full compatibility with Deltares API format for seamless data exchange
- **Measure Type System**: Predefined solution types with default properties
- **API Versioning**: Explicit versioning through paths and headers

## Core Concepts

### Nature-Based Solutions

Nature-based solutions (NbS) are the central concept of the API. They represent interventions that are inspired and supported by nature, providing environmental, social, and economic benefits.

In v2, NBS objects are enhanced with:
- GeoJSON geometry
- Visual styling properties
- Physical dimensions
- Specialized impact metrics
- Measure type references
- Calculated area and length properties

Example NBS object:
```json
{
  "id": 1,
  "name": "Urban Forest Corridor",
  "definition": "Row of trees planted along a street",
  "cobenefits": "Biodiversity, air quality, aesthetics",
  "specificdetails": "Includes native tree species only",
  "location": "Main Street",
  "geometry": {
    "type": "LineString",
    "coordinates": [[4.901, 52.369], [4.902, 52.368]]
  },
  "styling": {
    "color": "#00ff00",
    "hidden": false
  },
  "physical_properties": {
    "default_width": 5.0,
    "default_depth": 1.0
  },
  "area": 500,
  "length": 250,
  "measure_id": "15",
  "adaptations": [...],
  "impacts": [...]
}
```

### Measure Types

Measure types are predefined solution categories that provide default properties and configurations for NBS solutions. They enable consistent classification and provide default values for physical properties.

Example measure type:
```json
{
  "id": "39",
  "name": "Green Roof",
  "description": "Vegetated roof system for stormwater management",
  "default_color": "#31D336",
  "default_inflow": 1.0,
  "default_depth": 0.05,
  "default_width": 5.0,
  "default_radius": 1.0
}
```

### Enhanced Impacts

In v2, impacts can include specialized metrics for different categories:

```json
{
  "magnitude": 10.5,
  "unit": {"unit": "m2", "description": "shade"},
  "intensity": {"intensity": "medium"},
  "specialized": {
    "climate": {
      "temp_reduction": 2.5,
      "evapotranspiration": 20.0
    },
    "water_quality": {
      "filtering_unit": 45.0
    },
    "cost": {
      "construction_cost": 5000,
      "maintenance_cost": 500
    }
  }
}
```

### Projects

Projects are new in v2 and allow grouping multiple NBS solutions with common settings and targets:

```json
{
  "id": "proj-12345678",
  "title": "Urban Heat Island Mitigation",
  "description": "Reducing heat in the city center",
  "settings": {
    "scenario_name": "Summer Heat Wave",
    "capacity": {
      "heatCoping": true,
      "floodCoping": false
    },
    "soil": "sandy"
  },
  "targets": {
    "climate": {
      "temp_reduction": {
        "include": true,
        "value": "3.0"
      }
    }
  },
  "areas": [...]
}
```

## Deltares API Compatibility

The NBSAPI v2 is designed with full compatibility with the Deltares API format, enabling seamless data exchange with Deltares climate adaptation tools and other systems using the Deltares standard.

### Key Compatibility Features

- **Deltares Export Format**: Export projects in Deltares-compatible GeoJSON format
- **Field Name Mapping**: Automatic conversion between snake_case (API) and camelCase (Deltares)
- **Impact Data Flattening**: Convert specialized impacts to Deltares apiData structure
- **Measure Type Integration**: Support for Deltares measure type system
- **Project Settings**: Compatible project configuration and targets

### Export Example

Export a project in Deltares format:
```
GET /v2/api/projects/{id}/export/deltares
```

This returns a complete Deltares-compatible project with:
- All NBS areas as GeoJSON Features
- Project settings in Deltares format (scenarioName, capacity, etc.)
- Targets with camelCase field names
- Map configuration and measure overrides

### Field Mapping

The API automatically converts field names between formats:

| API v2 (snake_case) | Deltares (camelCase) |
|---------------------|---------------------|
| temp_reduction      | tempReduction       |
| construction_cost   | constructionCost    |
| maintenance_cost    | maintenanceCost     |
| cool_spot          | coolSpot            |
| capture_unit       | captureUnit         |
| filtering_unit     | filteringUnit       |
| settling_unit      | settlingUnit        |
| storage_capacity   | storageCapacity     |

## API Endpoints

### Nature-Based Solutions

- `GET /v2/api/solutions`: List all solutions
- `GET /v2/api/solutions/{id}`: Get a specific solution
- `GET /v2/api/solutions/{id}/geojson`: Get a solution as GeoJSON Feature
- `POST /v2/api/solutions?as_geojson=true`: Filter solutions (with optional GeoJSON response)
- `POST /v2/api/add_solution`: Create a new solution
- `PATCH /v2/api/solutions/{id}`: Update a solution

### Impacts

- `GET /v2/api/impacts/intensities`: List all impact intensities
- `GET /v2/api/impacts/units`: List all impact units
- `GET /v2/api/impacts/solutions/{id}/impacts`: Get enhanced impacts for a solution
- `GET /v2/api/impacts/{id}`: Get a specific impact with specialized data
- `POST /v2/api/solutions/{id}/impacts`: Add an impact to a solution

### Projects

- `GET /v2/api/projects`: List all projects
- `GET /v2/api/projects/{id}`: Get a specific project
- `POST /v2/api/projects`: Create a new project
- `PATCH /v2/api/projects/{id}`: Update a project
- `DELETE /v2/api/projects/{id}`: Delete a project
- `POST /v2/api/projects/{id}/solutions/{solution_id}`: Add solution to project
- `DELETE /v2/api/projects/{id}/solutions/{solution_id}`: Remove solution from project
- `POST /v2/api/projects/import`: Import a project
- `GET /v2/api/projects/{id}/export`: Export a project
- `GET /v2/api/projects/{id}/export/deltares`: Export a project in Deltares format

### Measure Types

- `GET /v2/api/measure_types`: List all measure types
- `GET /v2/api/measure_types/{id}`: Get a specific measure type
- `POST /v2/api/measure_types`: Create a new measure type
- `PATCH /v2/api/measure_types/{id}`: Update a measure type
- `DELETE /v2/api/measure_types/{id}`: Delete a measure type

## API Versioning

The API supports explicit versioning in multiple ways:

1. **Path-based versioning**: Use `/v1/` or `/v2/` in your API paths
2. **Header-based versioning**: Use the `Accept-Version` header
3. **Default versioning**: Requests without explicit version default to v2

For information about the current API version, use:
```
GET /api/version
```

## Authentication

Authentication works the same as in v1, using JWT tokens:

1. Obtain a token: `POST /auth/token`
2. Include the token in the `Authorization` header: `Bearer <token>`

## GeoJSON Support

The API supports three GeoJSON geometry types:

1. **Point**: A single point with coordinates `[longitude, latitude]`
2. **LineString**: A series of points forming a line
3. **Polygon**: A series of points forming a closed shape

Example GeoJSON response for a solution:
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[4.901, 52.369], [4.902, 52.368], [4.903, 52.369], [4.901, 52.369]]]
  },
  "properties": {
    "id": 1,
    "name": "Urban Rain Garden",
    "definition": "...",
    ...
  },
  "id": 1
}
```

## Further Documentation

- [Migration Guide](migration_guide_v1_to_v2.md): Guide for migrating from v1 to v2
