# Deltares API Usage Guide

This guide demonstrates how to create and retrieve nature-based solution resources using the API, based on the Deltares data format.

## Overview

The Deltares format includes various types of nature-based solutions with different geometries (Point, LineString, Polygon) and physical properties. Each solution has specific measures, styling, and impact data.

## Key Architectural Changes in v2

### ❌ Deprecated: Adaptation Targets (v1 approach)
```json
{
  "adaptations": [
    {"adaptation": {"type": "Heat"}, "value": 80},
    {"adaptation": {"type": "Pluvial Flooding"}, "value": 20}
  ]
}
```

### ✅ New: Specialized Impacts (v2 Deltares-compatible approach)
```json
{
  "impacts": [
    {
      "magnitude": 142.34,
      "unit": {"unit": "m3", "description": "storage capacity"},
      "intensity": {"intensity": "high"},
      "specialized": {
        "climate": {
          "temp_reduction": 0.057,
          "storage_capacity": 142.34,
          "evapotranspiration": 0.041
        }
      }
    }
  ]
}
```

### ✅ New: Project-Level Targets
```json
{
  "targets": {
    "climate": {
      "storage_capacity": {"include": true, "value": "1400"},
      "temp_reduction": {"include": true, "value": "0"}
    },
    "water_quality": {
      "filtering_unit": {"include": true, "value": "100"}
    }
  }
}
```

**Why this change?**
- **Quantitative vs Qualitative**: Specialized impacts provide measurable values rather than abstract scores
- **Deltares Compatibility**: Matches the Deltares data format exactly
- **Better Organization**: Separates solution-level impacts from project-level targets
- **Extensibility**: Easier to add new impact categories without schema changes

### Migration Guide: v1 → v2

| v1 Concept | v2 Replacement | Example |
|------------|----------------|---------|
| `adaptations: [{"type": "Heat", "value": 80}]` | **Specialized Climate Impact**: `{"climate": {"temp_reduction": 1.5}}` | Quantified temperature reduction |
| `adaptations: [{"type": "Flooding", "value": 60}]` | **Specialized Climate Impact**: `{"climate": {"storage_capacity": 500}}` | Actual storage capacity |
| Solution-level adaptation targets | **Project-level targets**: `{"targets": {"climate": {"temp_reduction": {"value": "2.0"}}}}` | Project-wide performance goals |
| Abstract scoring (0-100) | **Measurable units**: `{"unit": "m3", "magnitude": 142.34}` | Real-world measurements |

### Key Architectural Improvements

1. **Two-Level System**:
   - **Solution Level**: Specialized impacts with quantitative measurements
   - **Project Level**: Performance targets and goals

2. **Deltares Compatibility**: 
   - Direct mapping from Deltares `apiData` to specialized impacts
   - Project settings and targets from Deltares project structure

3. **Enhanced Measurement**:
   - Units and magnitudes for all metrics
   - Currency support for cost impacts
   - Negative values for losses (e.g., groundwater depletion)

## Language-Agnostic API Guide

This section provides examples using HTTP requests that can be implemented in any programming language.

### Creating a Nature-Based Solution

**Endpoint:** `POST /v2/api/solutions/add_solution`

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer {access_token}  # If authentication is required
```

**Request Body Schema (from OpenAPI spec):**
- `name` (string, required): Name of the solution
- `definition` (string, required): Definition of the solution
- `cobenefits` (string, required): Co-benefits description
- `specificdetails` (string, required): Specific details
- `location` (string, required): Location description
- `geometry` (object, optional): GeoJSON geometry (Point, LineString, Polygon, or GeometryCollection)
- `styling` (object, optional): Visual styling properties
  - `color` (string): Hex colour code (default: "#3388ff")
  - `hidden` (boolean): Hide on initial render (default: false)
- `physical_properties` (object, optional): Physical dimensions
  - `default_inflow`, `default_depth`, `default_width`, `default_radius` (number)
  - `area_inflow`, `area_depth`, `area_width`, `area_radius` (number)
- `area` (number, optional): Calculated area in square metres
- `impacts` (array): List of impacts with:
  - `magnitude` (number, required)
  - `unit` (object, required): `unit` and `description`
  - `intensity` (object, required): `intensity` string
- `adaptations` (array): List of adaptation targets

#### Example 1: Creating a Polygon-based Rain Garden

**HTTP Request:**
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

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "name": "Area-1",
  "definition": "Imported from Deltares format",
  "cobenefits": "Various environmental benefits",
  "specificdetails": "Details from Deltares import",
  "location": "Imported location",
  "geometry": { ... },
  "styling": { ... },
  "physical_properties": { ... },
  "area": 3672.3235347681,
  "impacts": [ ... ],
  "solution_targets": []
}
```

#### Example 2: Creating a LineString-based Bioswale

**HTTP Request:**
```http
POST /v2/api/solutions/add_solution HTTP/1.1
Host: your-api-host.com
Content-Type: application/json

{
  "name": "Area-4",
  "definition": "Bioswale for water management",
  "cobenefits": "Water filtration and habitat creation",
  "specificdetails": "Linear bioswale along roadway",
  "location": "Street drainage system",
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [23.716148279378956, 38.00875382311804],
      [23.71725307258484, 38.00937559547941],
      [23.71789424721402, 38.00984192129033]
    ]
  },
  "styling": {
    "color": "#31D336",
    "hidden": false
  },
  "physical_properties": {
    "default_inflow": 10,
    "default_depth": 0.35,
    "default_width": 1,
    "default_radius": 0.0001
  },
  "impacts": [
    {
      "magnitude": 68.38913509542978,
      "unit": {
        "unit": "m3",
        "description": "storage capacity"
      },
      "intensity": {
        "intensity": "low"
      }
    }
  ]
}
```

#### Example 3: Creating a Point-based Infiltration Well

**HTTP Request:**
```http
POST /v2/api/solutions/add_solution HTTP/1.1
Host: your-api-host.com
Content-Type: application/json

{
  "name": "Area-22",
  "definition": "Infiltration well for groundwater recharge",
  "cobenefits": "Groundwater replenishment",
  "specificdetails": "Deep infiltration well",
  "location": "Urban plaza",
  "geometry": {
    "type": "Point",
    "coordinates": [23.71905028688252, 38.009586258632595]
  },
  "styling": {
    "color": "#DB14D4",
    "hidden": false
  },
  "physical_properties": {
    "default_inflow": 20,
    "default_depth": 1,
    "default_width": 1,
    "default_radius": 1
  },
  "impacts": [
    {
      "magnitude": 3.141592653589793,
      "unit": {
        "unit": "m3",
        "description": "storage capacity"
      },
      "intensity": {
        "intensity": "low"
      }
    }
  ]
}
```

### Retrieving Solutions

#### Get All Solutions

**Endpoint:** `POST /v2/api/solutions/solutions`

**HTTP Request:**
```http
POST /v2/api/solutions/solutions HTTP/1.1
Host: your-api-host.com
Content-Type: application/json

{}
```

**Optional Request Body for Filtering:**
```json
{
  "targets": [
    {
      "adaptation": {"type": "Heat"},
      "value": 80
    }
  ],
  "intensities": [
    {"intensity": "medium"}
  ],
  "bbox": [-6.2757665, 53.332055, -6.274319, 53.332553]
}
```

#### Get Solutions as GeoJSON

**HTTP Request:**
```http
POST /v2/api/solutions/solutions?as_geojson=true HTTP/1.1
Host: your-api-host.com
Content-Type: application/json

{}
```

**Response:** GeoJSON FeatureCollection with all solutions

#### Get Specific Solution

**Endpoint:** `GET /v2/api/solutions/solutions/{solution_id}`

**HTTP Request:**
```http
GET /v2/api/solutions/solutions/1 HTTP/1.1
Host: your-api-host.com
```

#### Get Solution as GeoJSON Feature

**Endpoint:** `GET /v2/api/solutions/solutions/{solution_id}/geojson`

**HTTP Request:**
```http
GET /v2/api/solutions/solutions/1/geojson HTTP/1.1
Host: your-api-host.com
```

### Working with Impacts

#### Add Specialised Impact to Solution

**Endpoint:** `POST /v2/api/impacts/solutions/{solution_id}/impacts`

**HTTP Request for Climate Impact:**
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

**HTTP Request for Water Quality Impact:**
```http
POST /v2/api/impacts/solutions/1/impacts HTTP/1.1
Host: your-api-host.com
Content-Type: application/json
Authorization: Bearer your-access-token

{
  "magnitude": 1.8201316769232005,
  "unit": {
    "unit": "units",
    "description": "water quality improvement"
  },
  "intensity": {
    "intensity": "medium"
  },
  "specialized": {
    "water_quality": {
      "capture_unit": -0.2831315941880535,
      "filtering_unit": 1.8201316769232005,
      "settling_unit": 1.8403553622223476
    }
  }
}
```

**HTTP Request for Cost Impact:**
```http
POST /v2/api/impacts/solutions/1/impacts HTTP/1.1
Host: your-api-host.com
Content-Type: application/json
Authorization: Bearer your-access-token

{
  "magnitude": 58381.40474038341,
  "unit": {
    "unit": "EUR",
    "description": "construction cost"
  },
  "intensity": {
    "intensity": "high"
  },
  "specialized": {
    "cost": {
      "construction_cost": 58381.40474038341,
      "maintenance_cost": 245.20189990961032,
      "currency": "EUR"
    }
  }
}
```

### Creating Projects

**Endpoint:** `POST /v2/api/projects`

**HTTP Request:**
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
      "evapotranspiration": {
        "include": true,
        "value": "0"
      },
      "temp_reduction": {
        "include": true,
        "value": "0"
      },
      "cool_spot": {
        "include": true,
        "value": "0"
      }
    },
    "cost": {
      "construction_cost": {
        "include": true,
        "value": "0"
      },
      "maintenance_cost": {
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
      },
      "settling_unit": {
        "include": true,
        "value": "100"
      }
    }
  },
  "areas": [1, 2, 3]  // Solution IDs to include
}
```

### Import Complete Deltares Project

**Endpoint:** `POST /v2/api/projects/import`

This endpoint allows importing a complete project with all its solutions and settings in one request.

### Authentication

For endpoints requiring authentication, obtain an access token:

**Endpoint:** `POST /auth/token`

**HTTP Request:**
```http
POST /auth/token HTTP/1.1
Host: your-api-host.com
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=your-username&password=your-password
```

**Response:**
```json
{
  "access_token": "your-access-token",
  "token_type": "bearer"
}
```

## Error Responses

All endpoints follow standard HTTP status codes:
- `200 OK`: Successful retrieval
- `201 Created`: Successful creation
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

**Validation Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Implementation Notes

1. **Geometry Validation**: Ensure GeoJSON geometries follow the specification
   - Points: `[longitude, latitude]` array
   - LineStrings: Array of at least 2 coordinate pairs
   - Polygons: Array of linear rings, first ring is exterior

2. **Physical Properties**: All measurements in metric units
   - Depths, widths, radii: metres
   - Inflow rates: litres per second
   - Areas: square metres

3. **Measure IDs**: Use consistent measure type identifiers from Deltares
   - Reference the measure types section for valid IDs

4. **Impact Units**: Define appropriate units for each impact type
   - Storage capacity: "m3"
   - Temperature reduction: "°C"
   - Costs: Currency codes (EUR, USD, etc.)

---

## Python Implementation Examples

### 1. Polygon-based Solution (e.g., Rain Garden)

```python
import requests
from nbsapi.schemas.naturebasedsolution import NatureBasedSolutionCreate
from nbsapi.schemas.styling import StylingProperties
from nbsapi.schemas.physical_properties import PhysicalProperties
from nbsapi.schemas.impact import ImpactBase, ImpactUnit, ImpactIntensity

# Example: Creating a rain garden (measure 39)
solution = NatureBasedSolutionCreate(
    name="Area-1",
    definition="Imported from Deltares format",
    cobenefits="Various environmental benefits",
    specificdetails="Details from Deltares import",
    location="Imported location",
    geometry={
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
    styling=StylingProperties(
        color="#cfdd20",
        hidden=False
    ),
    physical_properties=PhysicalProperties(
        default_inflow=1,
        default_depth=0.05,
        default_width=5,
        default_radius=1,
        area_depth="0.05"
    ),
    measure_id="39",
    area=3672.3235347681,
    impacts=[
        ImpactBase(
            magnitude=10.0,
            unit=ImpactUnit(unit="m2", description="area"),
            intensity=ImpactIntensity(intensity="medium")
        )
    ]
)

# POST to API
response = requests.post(
    "http://localhost:8000/api/v2/nature-based-solutions",
    json=solution.model_dump()
)
created_solution = response.json()
```

### 2. LineString-based Solution (e.g., Bioswale)

```python
# Example: Creating a bioswale (measure 6)
bioswale = NatureBasedSolutionCreate(
    name="Area-4",
    definition="Imported from Deltares format",
    cobenefits="Various environmental benefits",
    specificdetails="Details from Deltares import",
    location="Imported location",
    geometry={
        "type": "LineString",
        "coordinates": [
            [23.716148279378956, 38.00875382311804],
            [23.71725307258484, 38.00937559547941],
            [23.71789424721402, 38.00984192129033]
        ]
    },
    styling=StylingProperties(
        color="#31D336",
        hidden=False
    ),
    physical_properties=PhysicalProperties(
        default_inflow=10,
        default_depth=0.35,
        default_width=1,
        default_radius=0.0001
    ),
    measure_id="6",
    length=133.4385512785903,  # For LineString geometries
    impacts=[
        ImpactBase(
            magnitude=68.38913509542978,
            unit=ImpactUnit(unit="m3", description="storage capacity"),
            intensity=ImpactIntensity(intensity="low")
        )
    ]
)

response = requests.post(
    "http://localhost:8000/api/v2/nature-based-solutions",
    json=bioswale.model_dump()
)
```

### 3. Point-based Solution (e.g., Infiltration Well)

```python
# Example: Creating an infiltration well (measure 37)
well = NatureBasedSolutionCreate(
    name="Area-22",
    definition="Imported from Deltares format",
    cobenefits="Various environmental benefits",
    specificdetails="Details from Deltares import",
    location="Imported location",
    geometry={
        "type": "Point",
        "coordinates": [23.71905028688252, 38.009586258632595]
    },
    styling=StylingProperties(
        color="#DB14D4",
        hidden=False
    ),
    physical_properties=PhysicalProperties(
        default_inflow=20,
        default_depth=1,
        default_width=1,
        default_radius=1
    ),
    measure_id="37",
    impacts=[
        ImpactBase(
            magnitude=3.141592653589793,
            unit=ImpactUnit(unit="m3", description="storage capacity"),
            intensity=ImpactIntensity(intensity="low")
        )
    ]
)

response = requests.post(
    "http://localhost:8000/api/v2/nature-based-solutions",
    json=well.model_dump()
)
```

## Retrieving Resources

### 1. Get All Solutions

```python
# Get all nature-based solutions
response = requests.get("http://localhost:8000/api/v2/nature-based-solutions")
solutions = response.json()

# Filter by measure type
measure_39_solutions = [s for s in solutions if s["measure_id"] == "39"]
```

### 2. Get Specific Solution

```python
# Get a specific solution by ID
solution_id = created_solution["id"]
response = requests.get(f"http://localhost:8000/api/v2/nature-based-solutions/{solution_id}")
solution = response.json()
```

### 3. Export to Deltares Format

```python
from nbsapi.utils.deltares_converter import convert_solution_to_deltares_feature

# Convert API solution to Deltares format
deltares_feature = convert_solution_to_deltares_feature(solution)

# The result includes the Deltares-specific fields
print(deltares_feature.properties.defaultInflow)  # 1
print(deltares_feature.properties.defaultDepth)   # 0.05
print(deltares_feature.properties.color)          # "#cfdd20"
```

## Deltares-Specific Properties

When creating solutions from Deltares data, the following properties are preserved:

### Physical Properties
- `defaultInflow`: Default inflow rate
- `defaultDepth`: Default depth (m)
- `defaultWidth`: Default width (m)
- `defaultRadius`: Default radius (m)
- `areaInflow`, `areaDepth`, `areaWidth`, `areaRadius`: Area-specific overrides

### API Data (Impact Metrics)
- `constructionCost`: Construction cost (€)
- `maintenanceCost`: Annual maintenance cost (€/year)
- `tempReduction`: Temperature reduction (°C)
- `coolSpot`: Cool spot indicator (0 or 1)
- `storageCapacity`: Water storage capacity (m³)
- `groundwater_recharge`: Groundwater recharge rate
- `evapotranspiration`: Evapotranspiration rate
- `captureUnit`, `filteringUnit`, `settlingUnit`: Water quality metrics

### Measure Types

Common measure IDs in the Deltares format:
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

## Complete Example: Import Deltares Project

```python
import json
from typing import List

def import_deltares_project(deltares_file_path: str) -> List[dict]:
    """Import a complete Deltares project."""
    with open(deltares_file_path) as f:
        deltares_data = json.load(f)
    
    created_solutions = []
    
    for area in deltares_data["areas"]:
        # Convert Deltares area to API solution
        solution = convert_deltares_to_api_solution(area)
        
        # Create via API
        response = requests.post(
            "http://localhost:8000/api/v2/nature-based-solutions",
            json=solution.model_dump()
        )
        
        if response.status_code == 201:
            created_solutions.append(response.json())
        else:
            print(f"Failed to create {area['properties']['name']}: {response.text}")
    
    return created_solutions

# Import the test data
solutions = import_deltares_project("tests/fixtures/deltares.json")
print(f"Imported {len(solutions)} solutions")
```

## Notes

1. The API preserves all Deltares-specific fields through the physical properties and impacts
2. Geometry types (Point, LineString, Polygon) are fully supported
3. Styling information (colour, visibility) is maintained
4. Area and length calculations are preserved for appropriate geometry types
5. The conversion maintains compatibility for round-trip operations (API → Deltares → API)