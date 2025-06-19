# API Version Differences: V1 vs V2

This document outlines the major differences between V1 and V2 APIs for retrieving solutions, adaptation targets, and impacts.

## Major Differences in Solution Retrieval

### V1 Approach
- Solutions use a simple POST endpoint `/v1/api/solutions/solutions` 
- Basic filtering with `SolutionRequest` schema
- Returns plain JSON array of solutions
- Limited to basic properties (name, definition, location, etc.)

### V2 Approach
- Enhanced POST endpoint `/v2/api/solutions/solutions` with optional `?as_geojson=true` parameter
- More sophisticated `SolutionRequestV2` schema
- Can return either JSON array OR GeoJSON FeatureCollection
- Includes rich geometric data (Point, LineString, Polygon, GeometryCollection)
- Additional endpoints for individual solutions as GeoJSON Features
- Enhanced with styling properties, physical properties, and calculated areas

## Adaptation Targets Comparison

### V1
- Solutions have `adaptations` field during creation and `solution_targets` when reading
- Basic `AdaptationTargetRead` structure with adaptation type and value (0-100)

### V2
- Maintains same `AdaptationTargetRead` structure
- Same filtering capabilities through `targets` parameter
- No major structural changes to adaptation targets themselves

## Impact System Differences

### V1
- Simple `ImpactBase` with magnitude, unit, and intensity
- Basic impact retrieval through solution objects
- Limited to general impact categories

### V2
- Enhanced `EnhancedImpactBase` with specialized impact categories
- Dedicated impact endpoints: `/v2/api/impacts/solutions/{solution_id}/impacts`
- Specialized impact types:
  - `ClimateImpact` (temperature reduction, evapotranspiration, storage capacity)
  - `WaterQualityImpact` (capture, filtering, settling units)
  - `CostImpact` (construction/maintenance costs with currency)
- Individual impact retrieval: `/v2/api/impacts/impacts/{impact_id}`

### V2 Advantages
1. **Output Formats**: V2 supports both JSON and GeoJSON output formats, while V1 only supports JSON
2. **Geometric Capabilities**: V2 includes full GeoJSON geometry support for precise spatial representation
3. **Impact Specialization**: V2 allows for domain-specific impact metrics rather than generic ones
4. **Physical Properties**: V2 includes detailed physical dimensions (depth, width, inflow rates)
5. **Styling**: V2 supports visual styling properties for rendering
6. **Project Management**: V2 introduces Projects concept for grouping solutions (entirely absent in V1)

### Where V1 Appears "Simpler"
- V1 has a flatter, simpler schema structure
- Fewer optional fields and nested objects
- More straightforward request/response patterns

However, this simplicity comes at the cost of functionality rather than flexibility. V2 maintains backward compatibility in core concepts while adding significant new capabilities for spatial applications and detailed impact analysis.

## Key Architectural Difference

The fundamental difference is that **V1 treats solutions as simple data records**, while **V2 treats them as spatial features** with detailed properties and specialized metrics.

V2 represents an evolution from basic data management to comprehensive spatially-enabled nature-based solution management with impact analysis capabilities.
