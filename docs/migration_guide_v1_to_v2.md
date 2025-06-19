# Migration Guide: NBSAPI v1 to v2

This guide explains how to migrate your applications from NBSAPI v1 to v2. The v2 API includes significant enhancements to better support complex nature-based solution data, including GeoJSON geometries, specialized impact metrics, physical properties, and project-level organization.

## API Versioning

The NBSAPI now supports explicit versioning in multiple ways:

1. **Path-based versioning**: Use `/v1/` or `/v2/` in your API paths
   ```
   // v1 endpoint
   GET /v1/api/solutions
   
   // v2 endpoint
   GET /v2/api/solutions
   ```

2. **Header-based versioning**: Use the `Accept-Version` header
   ```
   // Request v1 API
   GET /api/solutions
   Accept-Version: v1
   
   // Request v2 API
   GET /api/solutions
   Accept-Version: v2
   ```

3. **Default versioning**: Requests without explicit version default to v2

For information about the current API version, use:
```
GET /api/version
```

## Key Changes in v2

### 1. Deltares API Compatibility

The v2 API introduces full compatibility with the Deltares API format, enabling seamless data exchange with Deltares climate adaptation tools:

#### New in v2:
- Deltares export format (`/export/deltares` endpoint)
- Measure type system for predefined solution categories
- Automatic field name conversion (snake_case ↔ camelCase)
- Impact data flattening for Deltares apiData structure

#### Migration Example:
```javascript
// v2 - Export project in Deltares format
const response = await fetch('/v2/api/projects/proj-123/export/deltares');
const deltares_project = await response.json();
// Returns Deltares-compatible GeoJSON with all areas, settings, and targets

// v2 - Work with measure types
const measure_types = await fetch('/v2/api/measure_types');
console.log(measure_types);  // List of predefined solution types

// Create solution with measure type
const new_solution = {
  name: "Rain Garden",
  measure_id: "26",  // References a predefined measure type
  geometry: {...},
  ...
};
```

### 2. GeoJSON Support

The v2 API fully supports GeoJSON for geospatial data:

#### New in v2:
- `geometry` field in `NatureBasedSolution` objects that accepts GeoJSON (Point, LineString, Polygon)
- GeoJSON responses via the `as_geojson` query parameter
- Calculated `area` field for polygon geometries

#### Migration Example:
```javascript
// v1 - Limited geometry support
const response = await fetch('/v1/api/solutions/1');
const solution = await response.json();
// No standard geometry format

// v2 - Full GeoJSON support
const response = await fetch('/v2/api/solutions/1');
const solution = await response.json();
console.log(solution.geometry);  // GeoJSON object

// v2 - Get solution as GeoJSON Feature
const response = await fetch('/v2/api/solutions/1/geojson');
const featureObject = await response.json();
// Full GeoJSON Feature with properties
```

### 2. Specialized Impact Types

The v2 API introduces specialized impact categories for more detailed metrics:

#### New in v2:
- Climate impacts (temperature reduction, evapotranspiration, etc.)
- Water quality impacts (filtering, capture, settling units)
- Cost impacts (construction, maintenance costs)

#### Migration Example:
```javascript
// v1 - Generic impacts
const impacts = solution.impacts;
// Only basic magnitude, unit, intensity

// v2 - Specialized impacts
const response = await fetch('/v2/api/solutions/1');
const solution = await response.json();
const specializedImpacts = solution.impacts.map(impact => impact.specialized);
console.log(specializedImpacts.climate);  // Climate-specific metrics
console.log(specializedImpacts.waterQuality);  // Water quality metrics
console.log(specializedImpacts.cost);  // Cost-related metrics
```

### 3. Physical Properties

The v2 API adds support for physical dimensions and properties:

#### New in v2:
- Default measurements (width, depth, radius, inflow)
- Area-specific measurements

#### Migration Example:
```javascript
// v1 - No physical properties

// v2 - Physical properties
const response = await fetch('/v2/api/solutions/1');
const solution = await response.json();
console.log(solution.physical_properties);  // Physical dimensions
```

### 4. Project Support

The v2 API introduces a completely new Project concept for organizing multiple NBS solutions:

#### New in v2:
- Project endpoints for creating and managing collections of solutions
- Project settings and targets
- Map display properties

#### Migration Example:
```javascript
// v1 - No project concept

// v2 - Create a project with multiple solutions
const newProject = {
  title: "Urban Heat Island Mitigation",
  description: "Project to reduce heat in the city center",
  areas: [1, 2, 3]  // Solution IDs
};

const response = await fetch('/v2/api/projects', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(newProject)
});

const project = await response.json();
console.log(project.id);  // Project ID for future reference
```

## Endpoint Changes

### New v2 Endpoints

| Endpoint | Description |
|----------|-------------|
| `/v2/api/solutions/{id}/geojson` | Get a solution as a GeoJSON Feature |
| `/v2/api/impacts/solutions/{id}/impacts` | Get enhanced impacts with specialized data |
| `/v2/api/projects` | Project management endpoints |
| `/v2/api/projects/{id}/solutions/{solution_id}` | Add/remove solutions from projects |
| `/v2/api/projects/import` and `/export` | Import/export project data |
| `/v2/api/projects/{id}/export/deltares` | Export project in Deltares format |
| `/v2/api/measure_types` | Manage predefined solution types |

### Modified v2 Endpoints

| v1 Endpoint | v2 Equivalent | Changes |
|-------------|---------------|---------|
| `/v1/api/solutions` | `/v2/api/solutions` | Added GeoJSON, styling, physical properties |
| `/v1/api/solutions/{id}` | `/v2/api/solutions/{id}` | Enhanced with additional properties |
| `/v1/api/impacts` | `/v2/api/impacts` | Enhanced with specialized impact types |

## Client Library Updates

If you're using client libraries to interact with the NBSAPI, you'll need to update them to v2. The basic structure is similar, but with enhanced capabilities:

```javascript
// v1 client library example
import { NbsApiClient } from 'nbsapi-client';
const client = new NbsApiClient('https://api.example.com');
const solutions = await client.getSolutions();

// v2 client library example
import { NbsApiClient } from 'nbsapi-client';
const client = new NbsApiClient('https://api.example.com', { version: 'v2' });
const solutions = await client.getSolutions();
const projects = await client.getProjects();  // New in v2
```

## Backward Compatibility

The v1 API will remain available for a transition period, but we recommend migrating to v2 to take advantage of the new features. The v1 API is now considered deprecated and will eventually be removed.

## Migration Steps

1. Update your API client to use the `v2` prefix or `Accept-Version: v2` header
2. Update your data models to handle the enhanced schemas
3. Consider using the new Project endpoints for organizing your solutions
4. Take advantage of the specialized impact types for more detailed metrics
5. Use GeoJSON for all geospatial data
6. Integrate measure types for consistent solution categorization
7. Utilize Deltares export for compatibility with Deltares tools


This is a living document and will be updated as the API evolves. Last updated: May 2025.
