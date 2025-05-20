## Analysis of input GeoJSON and existing OpenAPI specification

### 1. OpenAPI Specification (nbsapi.json)

Key components of current API include:

- **Authentication**: JWT token-based auth system
- **Nature-Based Solutions**: Core concept with endpoints to create and retrieve solutions
- **Adaptation Targets**: Define types of adaptation (heat, flooding, etc.) with values 0-100
- **Impacts**: Describe adaptation impacts with magnitude, unit, and intensity

The API currently uses a relatively simple model for NBS with basic properties like name, definition, location, and associated impacts and adaptation targets.

### 2. Votris GeoJSON Data (votris.geojson)

The Votris data represents a more complex and specialized implementation of nature-based solutions with:

- **Spatial geometry**: Areas defined as polygons, points, and linestrings with coordinates
- **Detailed properties**: Each area includes extensive metadata like:
  - Costs (construction, maintenance)
  - Environmental metrics (temperature reduction, evapotranspiration, etc.)
  - Storage capacity
  - Water-related parameters (groundwater recharge, filtering units)
  - Visual properties (color)
  - Physical dimensions (depth, width, radius)

The data is more specialized than what the current API supports, with a focus on hydrological and climate adaptation properties specifically.

## Key Gaps Between the API and GeoJSON

1. **Spatial representation**: The current API doesn't have robust GeoJSON support for geometries
2. **Quantitative metrics**: The API's impact model is simpler than the detailed metrics in Votris
3. **Visual representation**: The API lacks support for visual styling properties
4. **Dimensioning**: The API doesn't have fields for physical dimensions
5. **Project-level aggregation**: The Votris data has project-level settings and targets

## Proposed Evolution Plan for the API

### Phase 1: Extend Core Data Models

1. **Enhance the `NatureBasedSolutionRead` and `NatureBasedSolutionCreate` schemas**:
   - Add GeoJSON geometry support (Point, LineString, Polygon)
   - Add area calculation field
   - Add styling properties (color, visibility)

```json
{
  "geometry": {
    "type": "object",
    "title": "Geometry",
    "description": "GeoJSON geometry representation",
    "required": ["type", "coordinates"],
    "properties": {
      "type": {
        "type": "string",
        "enum": ["Point", "LineString", "Polygon"],
        "title": "Type"
      },
      "coordinates": {
        "type": "array",
        "title": "Coordinates"
      }
    }
  },
  "area": {
    "type": "number",
    "title": "Area",
    "description": "Calculated area in square meters"
  },
  "styling": {
    "type": "object",
    "properties": {
      "color": {
        "type": "string",
        "title": "Color",
        "description": "Hex color code for rendering"
      },
      "hidden": {
        "type": "boolean",
        "title": "Hidden",
        "default": false
      }
    }
  }
}
```

2. **Create more specialized impact types**:
   - Expand `ImpactBase` to include specialized subtypes
   - Add support for categories like climate, water quality, and costs

```json
{
  "ClimateImpact": {
    "properties": {
      "tempReduction": {
        "type": "number",
        "title": "Temperature Reduction"
      },
      "coolSpot": {
        "type": "number",
        "title": "Cool Spot"
      },
      "evapotranspiration": {
        "type": "number",
        "title": "Evapotranspiration"
      },
      "groundwater_recharge": {
        "type": "number",
        "title": "Groundwater Recharge"
      },
      "storageCapacity": {
        "type": "number",
        "title": "Storage Capacity"
      }
    }
  },
  "WaterQualityImpact": {
    "properties": {
      "captureUnit": {
        "type": "number",
        "title": "Capture Unit"
      },
      "filteringUnit": {
        "type": "number",
        "title": "Filtering Unit"
      },
      "settlingUnit": {
        "type": "number",
        "title": "Settling Unit"
      }
    }
  },
  "CostImpact": {
    "properties": {
      "constructionCost": {
        "type": "number",
        "title": "Construction Cost"
      },
      "maintenanceCost": {
        "type": "number",
        "title": "Maintenance Cost"
      }
    }
  }
}
```

3. **Add physical properties support**:
   - Create schemas for dimensional properties

```json
{
  "PhysicalProperties": {
    "properties": {
      "defaultInflow": {
        "type": "number",
        "title": "Default Inflow"
      },
      "defaultDepth": {
        "type": "number",
        "title": "Default Depth"
      },
      "defaultWidth": {
        "type": "number",
        "title": "Default Width"
      },
      "defaultRadius": {
        "type": "number",
        "title": "Default Radius"
      },
      "areaInflow": {
        "type": ["number", "null"],
        "title": "Area Inflow"
      },
      "areaDepth": {
        "type": ["number", "string", "null"],
        "title": "Area Depth"
      },
      "areaWidth": {
        "type": ["number", "null"],
        "title": "Area Width"
      },
      "areaRadius": {
        "type": ["number", "null"],
        "title": "Area Radius"
      }
    }
  }
}
```

### Phase 2: Add Project-Level Endpoints

1. **Create a Project schema**:
   - Support for project areas and their settings
   - Aggregate multiple NBS in a single project

```json
{
  "Project": {
    "properties": {
      "id": {
        "type": "string",
        "title": "ID"
      },
      "title": {
        "type": "string",
        "title": "Title"
      },
      "areas": {
        "type": "array",
        "items": {
          "$ref": "#/components/schemas/NatureBasedSolutionRead"
        },
        "title": "NBS Areas"
      },
      "settings": {
        "$ref": "#/components/schemas/ProjectSettings"
      },
      "map": {
        "$ref": "#/components/schemas/MapSettings"
      },
      "targets": {
        "$ref": "#/components/schemas/ProjectTargets"
      }
    },
    "required": ["id", "title", "areas"]
  }
}
```

2. **Add Project Settings schema**:
   - Support for scenario settings and project area properties

```json
{
  "ProjectSettings": {
    "properties": {
      "scenarioName": {
        "type": "string",
        "title": "Scenario Name"
      },
      "capacity": {
        "type": "object",
        "properties": {
          "heatCoping": {
            "type": "boolean"
          },
          "droughtCoping": {
            "type": "boolean"
          },
          "floodCoping": {
            "type": "boolean"
          },
          "waterSafetyCoping": {
            "type": "boolean"
          }
        }
      },
      "multifunctionality": {
        "type": "string"
      },
      "scale": {
        "type": "object",
        "properties": {
          "city": {
            "type": "boolean"
          },
          "neighbourhood": {
            "type": "boolean"
          },
          "street": {
            "type": "boolean"
          },
          "building": {
            "type": "boolean"
          }
        }
      },
      "suitability": {
        "type": "object",
        "properties": {
          "greySpace": {
            "type": "boolean"
          },
          "greenSpacePrivateGardens": {
            "type": "boolean"
          },
          "greenSpaceNoRecreation": {
            "type": "boolean"
          },
          "greenSpaceRecreationUrbanFarming": {
            "type": "boolean"
          },
          "greyGreenSpaceSportsPlayground": {
            "type": "boolean"
          },
          "redSpace": {
            "type": "boolean"
          },
          "blueSpace": {
            "type": "boolean"
          }
        }
      },
      "subsurface": {
        "type": "string"
      },
      "surface": {
        "type": "string"
      },
      "soil": {
        "type": "string"
      },
      "slope": {
        "type": "string"
      }
    }
  }
}
```

3. **Add Project Targets schema**:
   - Support for project-level targets and thresholds

```json
{
  "ProjectTargets": {
    "properties": {
      "climate": {
        "type": "object",
        "properties": {
          "storageCapacity": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          },
          "groundwater_recharge": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          },
          "evapotranspiration": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          },
          "tempReduction": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          },
          "coolSpot": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          }
        }
      },
      "cost": {
        "type": "object",
        "properties": {
          "constructionCost": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          },
          "maintenanceCost": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          }
        }
      },
      "waterquality": {
        "type": "object",
        "properties": {
          "filteringUnit": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          },
          "captureUnit": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          },
          "settlingUnit": {
            "type": "object",
            "properties": {
              "include": {
                "type": "boolean"
              },
              "value": {
                "type": "string"
              }
            }
          }
        }
      }
    }
  }
}
```

### Phase 3: Add New Endpoints

1. **Project Management Endpoints**:
   ```
   GET /v2/api/projects
   GET /v2/api/projects/{project_id}
   POST /v2/api/projects
   PUT /v2/api/projects/{project_id}
   DELETE /v2/api/projects/{project_id}
   ```

2. **Measure Type Reference Endpoints**:
   ```
   GET /v2/api/measure_types
   POST /v2/api/measure_types
   ```

3. **Analysis Endpoints**:
   ```
   GET /v2/api/projects/{project_id}/analysis
   POST /v2/api/projects/{project_id}/calculations
   ```

4. **Export/Import Endpoints**:
   ```
   GET /v2/api/projects/{project_id}/export
   POST /v2/api/projects/import
   ```

## Detailed API Evolution Plan

### 1. Maintain Backward Compatibility

- Create a `/v2` namespace for all new endpoints
- Keep existing v1 endpoints functional
- Add version negotiation to support both v1 and v2 clients

### 2. Extend the Data Models

```json
{
  "MeasureType": {
    "properties": {
      "id": {
        "type": "string"
      },
      "name": {
        "type": "string"
      },
      "description": {
        "type": "string"
      },
      "defaultProperties": {
        "type": "object"
      }
    }
  },
  "NatureBasedSolutionReadV2": {
    "allOf": [
      {
        "$ref": "#/components/schemas/NatureBasedSolutionRead"
      },
      {
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "measure": {
            "type": "string",
            "description": "Reference to measure type"
          },
          "geometry": {
            "$ref": "#/components/schemas/Geometry"
          },
          "properties": {
            "type": "object",
            "properties": {
              "apiData": {
                "$ref": "#/components/schemas/ApiData"
              },
              "styling": {
                "$ref": "#/components/schemas/Styling"
              },
              "physical": {
                "$ref": "#/components/schemas/PhysicalProperties"
              }
            }
          }
        }
      }
    ]
  },
  "ApiData": {
    "properties": {
      "climate": {
        "$ref": "#/components/schemas/ClimateImpact"
      },
      "waterQuality": {
        "$ref": "#/components/schemas/WaterQualityImpact"
      },
      "cost": {
        "$ref": "#/components/schemas/CostImpact"
      }
    }
  }
}
```

### 3. Implementation Plan

1. **Documentation Updates**:
   - Create migration guides for v1 to v2
   - Update API reference documentation
   - Add examples for the new endpoints

2. **API Versioning Strategy**:
   - Use a version header for negotiation
   - Allow explicit version in URL path
   - Support automatic content negotiation

## Conclusion

The evolution from the current NBSAPI (v1) to support the complex Votris GeoJSON structure requires significant extensions to the data model and new endpoints. The key focus areas are:

1. Support for GeoJSON geometries and spatial properties
2. More detailed impact types for climate, water quality, and costs
3. Project-level structures for managing collections of NBS
4. Specialized analysis and calculation endpoints

With these changes, the API would be capable of handling the rich data structure in the Votris GeoJSON while maintaining backward compatibility with existing clients.
