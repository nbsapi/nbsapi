from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from nbsapi.config import settings


def create_docs_router() -> APIRouter:
    """
    Create a router for versioned API documentation

    This creates custom Swagger UI and ReDoc interfaces for different API versions.
    It returns version-specific OpenAPI schemas that filter routes by their version.
    """
    router = APIRouter()

    # Helper to filter routes by version prefix
    def filter_routes_by_version(app, version_prefix="/v1"):
        filtered_routes = []
        for route in app.routes:
            # Check if this route belongs to the version we want
            # Includes both /v1/ and nested routes like /v1/api/...
            if hasattr(route, "path") and route.path.startswith(version_prefix):
                filtered_routes.append(route)  # noqa: PERF401

        # Also include core routes like /auth/token that belong to all versions
        for route in app.routes:
            if (
                hasattr(route, "path")
                and not route.path.startswith("/v1")
                and not route.path.startswith("/v2")
                and not route.path.startswith("/docs")
                and not route.path.startswith("/redoc")
                and not route.path.startswith("/openapi.json")
            ):
                filtered_routes.append(route)  # noqa: PERF401

        return filtered_routes

    # Default to the v2 docs
    @router.get("/docs", include_in_schema=False)
    async def get_default_docs(request: Request):
        return get_swagger_ui_html(
            openapi_url="/v2/openapi.json",
            title=f"{settings.project_name} API (v2) - Click 'Models' at the bottom for schema definitions",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
            swagger_ui_parameters={
                "defaultModelsExpandDepth": 0,  # Show schemas section but collapse by default
                "docExpansion": "list",  # Show all operations collapsed
                "syntaxHighlight.theme": "monokai",
                "persistAuthorization": True,  # Keep auth between refreshes
                "deepLinking": True,  # Enable deep linking for better navigation
                "filter": True,  # Enable filtering operations
            },
        )

    # V1 Swagger UI
    @router.get("/v1/docs", include_in_schema=False)
    async def get_v1_docs(request: Request):
        return get_swagger_ui_html(
            openapi_url="/v1/openapi.json",
            title=f"{settings.project_name} API (v1) - Click 'Models' at the bottom for schema definitions",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
            swagger_ui_parameters={
                "defaultModelsExpandDepth": 0,  # Show schemas section but collapse by default
                "docExpansion": "list",  # Show all operations collapsed
                "syntaxHighlight.theme": "monokai",
                "persistAuthorization": True,  # Keep auth between refreshes
                "deepLinking": True,  # Enable deep linking for better navigation
                "filter": True,  # Enable filtering operations
            },
        )

    # V2 Swagger UI
    @router.get("/v2/docs", include_in_schema=False)
    async def get_v2_docs(request: Request):
        return get_swagger_ui_html(
            openapi_url="/v2/openapi.json",
            title=f"{settings.project_name} API (v2) - Click 'Models' at the bottom for schema definitions",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
            swagger_ui_parameters={
                "defaultModelsExpandDepth": 0,  # Show schemas section but collapse by default
                "docExpansion": "list",  # Show all operations collapsed
                "syntaxHighlight.theme": "monokai",
                "persistAuthorization": True,  # Keep auth between refreshes
                "deepLinking": True,  # Enable deep linking for better navigation
                "filter": True,  # Enable filtering operations
            },
        )

    # Default ReDoc to v2
    @router.get("/redoc", include_in_schema=False)
    async def get_default_redoc(request: Request):
        return get_redoc_html(
            openapi_url="/v2/openapi.json",
            title=f"{settings.project_name} API (v2)",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        )

    # V1 ReDoc
    @router.get("/v1/redoc", include_in_schema=False)
    async def get_v1_redoc(request: Request):
        return get_redoc_html(
            openapi_url="/v1/openapi.json",
            title=f"{settings.project_name} API (v1)",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        )

    # V2 ReDoc
    @router.get("/v2/redoc", include_in_schema=False)
    async def get_v2_redoc(request: Request):
        return get_redoc_html(
            openapi_url="/v2/openapi.json",
            title=f"{settings.project_name} API (v2)",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        )

    # Endpoint to generate v1 OpenAPI schema
    @router.get("/v1/openapi.json", include_in_schema=False)
    async def get_v1_openapi(request: Request):
        app = request.app
        v1_routes = filter_routes_by_version(app, "/v1")

        return JSONResponse(
            get_openapi(
                title=f"{settings.project_name} API (v1)",
                version="1.0.0",
                description="""## NBSAPI v1

An API for interoperability between digital tools that help to build and manage
nature-based solutions in the built and natural environment.

> **Version Navigation:**
> - Current: **v1 API** (basic functionality)
> - <a href="/v2/docs">Switch to v2 API</a> (enhanced with GeoJSON and Projects)
>
> The "Servers" dropdown shows the base URL for API requests.

### Key Concepts

#### Nature Based Solutions

Solutions that are inspired and supported by nature, which are cost-effective, **simultaneously provide environmental, social and economic benefits** and **help build resilience**.

Such solutions bring more, and more diverse, nature and natural features and processes into cities, landscapes and seascapes, through **locally adapted, resource-efficient and systemic interventions**.

The v1 API provides basic properties for solutions:
- **Name and Definition**: Descriptive metadata about the solution
- **Cobenefits**: Additional benefits the solution provides beyond its primary adaptation purpose
- **Specific Details**: Technical details specific to the implementation
- **Location**: Where the solution is implemented

#### Adaptation Targets

Adaptation targets define and quantify the type of adaptation facilitated by a **Nature-Based Solution**, each target having an associated value 0 - 100.

Each **NbS** may have **one or more** adaptation targets. As a tool builder, you specify the adaptation target for your service.

Example adaptation types:
- **Heat**: Adapting to increased urban heat stress
- **Pluvial Flooding**: Adapting to surface water flooding from heavy rainfall
- **Drought**: Adapting to water scarcity and drought conditions

#### Impacts

These are the adaptation impacts of **Nature-Based Solutions**. An impact has a **magnitude**, an **ImpactIntensity**, and an associated **ImpactUnit**, which may describe e.g. area or volume.

Impact parameters:
- **Magnitude**: Quantitative measurement of the impact
- **Unit**: The unit of measurement (e.g., m², m³, °C)
- **Intensity**: Qualitative assessment (low, medium, high)

For the enhanced v2 API with GeoJSON support, specialized impact types, and project management, <a href="/v2/docs">see the v2 documentation</a>.
""",
                routes=v1_routes,
                servers=[{"url": "", "description": "NBSAPI v1 Endpoints"}],
            )
        )

    # Endpoint to generate v2 OpenAPI schema
    @router.get("/v2/openapi.json", include_in_schema=False)
    async def get_v2_openapi(request: Request):
        app = request.app
        v2_routes = filter_routes_by_version(app, "/v2")

        return JSONResponse(
            get_openapi(
                title=f"{settings.project_name} API (v2)",
                version="2.0.0",
                description="""## NBSAPI v2

An API for interoperability between digital tools that help to build and 
manage nature-based solutions, with Deltares format compatibility.

> **Version Navigation:**
> - <a href="/v1/docs">Switch to v1 API</a>
> - Current: **v2 API** (includes GeoJSON and Projects)
> 
> The "Servers" dropdown shows the base URL for API requests.

### Key Concepts

#### Nature Based Solutions

Solutions that are inspired and supported by nature, which are cost-effective, **simultaneously provide environmental, social and economic benefits** and **help build resilience**.

v2 features:
- **GeoJSON Geometry**: Solution boundaries as standardized GeoJSON (Point, LineString, Polygon)
- **Styling Properties**: Visual appearance configuration with colour and visibility options
- **Physical Properties**: Physical dimensions like depth, width, and inflow rates
- **Deltares Compatibility**: Direct import/export with Deltares format

#### Specialized Impacts

Enhanced impact system that **extends** v1's basic impacts with quantitative domain-specific measurements:

**Dual-Layer Architecture:**
- **Basic Layer** (preserved from v1): magnitude, unit, intensity for general display and backward compatibility
- **Specialized Layer** (new in v2): domain-specific metrics for detailed analysis

**Specialized Impact Categories:**
- **Climate Impacts**: Temperature reduction (°C), cool spots, evapotranspiration (mm/day), groundwater recharge (mm/day), storage capacity (m³)
- **Water Quality Impacts**: Capture efficiency, filtering capacity, settling rates
- **Cost Impacts**: Construction and maintenance costs with currency specification

**Use Cases:**
- Basic impacts: Simple dashboards, general reporting, lightweight integrations
- Specialized impacts: Climate modeling, Deltares integration, scientific analysis

Each impact includes both basic impact data AND optional specialized data, allowing systems to choose their level of detail without breaking compatibility.

#### Projects

Projects organize multiple Nature-Based Solutions with shared settings and performance targets:

- **Project Settings**: Scenario configurations (capacity, scale, suitability)
- **Performance Targets**: Quantitative goals for climate, water quality, and costs
- **Map Configuration**: Center coordinates, zoom levels, base layers
- **Solution Collections**: Multiple solutions working together

Projects support Deltares import/export and provide project-wide performance tracking.

### Architecture Change: v1 → v2

**v1 Approach:**
```json
{"adaptations": [{"type": "Heat", "value": 80}]}
```

**v2 Enhanced Approach:**
```json
{
  "magnitude": 142.34,
  "unit": {"unit": "m3", "description": "storage capacity"},
  "intensity": {"intensity": "high"},
  "specialized": {
    "climate": {"temp_reduction": 1.5, "storage_capacity": 142.34}
  }
}
```

**Key Improvements:**
- **Preserved**: Basic impact structure (magnitude, unit, intensity) for backward compatibility
- **Enhanced**: Added specialized impact categories for detailed scientific analysis
- **Flexible**: Systems can use basic impacts only, specialized impacts only, or both together
- **Quantitative**: Measurable data instead of abstract scores enables better integration with climate modeling tools and Deltares systems
""",  # noqa: W291
                routes=v2_routes,
                servers=[{"url": "", "description": "NBSAPI v2 Endpoints"}],
            )
        )

    # Default OpenAPI JSON now returns v2 schema
    @router.get("/openapi.json", include_in_schema=False)
    async def get_default_openapi(request: Request):
        return await get_v2_openapi(request)

    return router
