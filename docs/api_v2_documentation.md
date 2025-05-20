# NBSAPI v2 Documentation

This document provides an overview of the NBSAPI v2, an API for interoperability between digital tools that help build and manage nature-based solutions (NbS) in the built and natural environment.

## Overview

The NBSAPI v2 extends the core concepts of v1 with richer data models, GeoJSON support, and project-level organization. It's designed to support complex NbS tools and integrations with specialized environmental metrics.

## Key Features of v2

- **Full GeoJSON Support**: Define the geometry of solutions using GeoJSON
- **Specialized Impact Metrics**: Detailed impact measurements for climate, water quality, and costs
- **Physical Properties**: Define physical dimensions of solutions
- **Project Management**: Group solutions into projects with targets and settings
- **API Versioning**: Explicit versioning through paths and headers

## Core Concepts

### Nature-Based Solutions

Nature-based solutions (NbS) are the central concept of the API. They represent interventions that are inspired and supported by nature, providing environmental, social, and economic benefits.

In v2, NBS objects are enhanced with:
- GeoJSON geometry
- Visual styling properties
- Physical dimensions
- Specialized impact metrics

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
  "adaptations": [...],
  "impacts": [...]
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
- [API Reference](api_reference_v2.md): Detailed API reference
- [Examples](examples_v2.md): Code examples for common tasks

## Support

If you need assistance, please contact support@nbsapi.org
