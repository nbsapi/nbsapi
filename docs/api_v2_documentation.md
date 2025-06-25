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

### Enhanced Impacts Architecture

V2 introduces a **dual-layer impact system** that extends v1's basic impacts with specialized domain-specific metrics:

#### Dual-Layer Architecture

**Basic Layer (preserved from v1):**
- Fundamental impact data: magnitude, unit, intensity
- Used for general-purpose display and backward compatibility
- Suitable for simple dashboards and lightweight integrations

**Specialized Layer (new in v2):**
- Domain-specific metrics for detailed scientific analysis
- Categories: climate, water quality, and cost impacts
- Used for climate modeling, Deltares integration, and advanced analytics

#### Why Both Layers?

1. **Backward Compatibility**: Existing V1 integrations continue to work without changes
2. **Progressive Enhancement**: Systems can adopt specialized impacts incrementally
3. **Use Case Differentiation**: Different tools need different levels of detail
4. **Flexibility**: A single impact can serve both simple visualization and complex modeling needs

#### Complete Impact Example

```json
{
  "magnitude": 142.34,
  "unit": {"unit": "m3", "description": "storage capacity"},
  "intensity": {"intensity": "high"},
  "specialized": {
    "climate": {
      "temp_reduction": 1.5,
      "cool_spot": 0,
      "evapotranspiration": 0.041,
      "groundwater_recharge": -0.043,
      "storage_capacity": 142.34
    },
    "water_quality": {
      "capture_unit": -0.283,
      "filtering_unit": 1.820,
      "settling_unit": 1.840
    },
    "cost": {
      "construction_cost": 58381.40,
      "maintenance_cost": 245.20,
      "currency": "EUR"
    }
  }
}
```

#### Impact Categories

**Climate Impacts:**
- `temp_reduction`: Temperature reduction in degrees Celsius
- `cool_spot`: Cool spot indicator (0 or 1)
- `evapotranspiration`: Evapotranspiration rate in mm/day
- `groundwater_recharge`: Groundwater recharge rate in mm/day (negative = loss)
- `storage_capacity`: Water storage capacity in cubic meters

**Water Quality Impacts:**
- `capture_unit`: Pollutant capture efficiency
- `filtering_unit`: Water filtration effectiveness
- `settling_unit`: Sedimentation effectiveness

**Cost Impacts:**
- `construction_cost`: Construction cost in currency units
- `maintenance_cost`: Annual maintenance cost
- `currency`: Currency code (EUR, USD, etc.)

#### Migration Strategy

**From V1 to V2:**
- Keep existing basic impacts for compatibility
- Add specialized impacts for enhanced functionality
- Systems can choose their level of detail

**Example Evolution:**
```json
// V1 Basic Impact (still supported in V2)
{
  "magnitude": 10.5,
  "unit": {"unit": "m2", "description": "shade"},
  "intensity": {"intensity": "medium"}
}

// V2 Enhanced Impact (adds specialized data)
{
  "magnitude": 10.5,
  "unit": {"unit": "m2", "description": "shade"},
  "intensity": {"intensity": "medium"},
  "specialized": {
    "climate": {
      "temp_reduction": 2.5,
      "storage_capacity": 10.5
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
