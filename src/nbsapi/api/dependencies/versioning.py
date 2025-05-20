from enum import Enum

from fastapi import Header, HTTPException, Request, status
from fastapi.responses import RedirectResponse


class ApiVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"


async def get_api_version(
    request: Request, accept_version: str | None = Header(None, alias="Accept-Version")
) -> ApiVersion:
    """
    Determine the API version to use based on headers or path

    Priority:
    1. Accept-Version header (if provided)
    2. Path-based version (if in the path)
    3. Default to latest version
    """
    # First check the Accept-Version header
    if accept_version:
        if accept_version.lower() == "v1":
            return ApiVersion.V1
        elif accept_version.lower() == "v2":
            return ApiVersion.V2
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Unsupported API version requested: {accept_version}",
            )

    # Then check the path
    path = request.url.path
    if "/v1/" in path:
        return ApiVersion.V1
    elif "/v2/" in path:
        return ApiVersion.V2

    # Default to the latest version
    return ApiVersion.V2


class VersionNegotiationMiddleware:
    """
    Middleware to handle API version negotiation

    This middleware redirects requests without an explicit version to the appropriate
    versioned endpoint based on the Accept-Version header or default version.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get the request path
        path = scope["path"]

        # Skip middleware for paths that already have a version
        if path.startswith("/v1/") or path.startswith("/v2/"):
            await self.app(scope, receive, send)
            return

        # Skip middleware for static files and non-API routes
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        # Skip middleware for global API endpoints that shouldn't be versioned
        if path in ["/api/version"]:
            await self.app(scope, receive, send)
            return

        # Get the Accept-Version header
        headers = dict(scope["headers"])
        accept_version = headers.get(b"accept-version", b"").decode()

        # Determine the version to use
        if accept_version.lower() == "v1":
            version = "v1"
        else:
            # Default to the latest version
            version = "v2"

        # Create a new path with the version
        new_path = f"/{version}{path}"

        # Create a redirect response
        redirect_url = f"{new_path}"
        if scope.get("query_string"):
            query_string = scope["query_string"].decode()
            redirect_url = f"{redirect_url}?{query_string}"

        # Create a redirect response
        response = RedirectResponse(url=redirect_url)

        # Convert the response to ASGI messages
        response_scope = scope.copy()
        response_scope["path"] = new_path
        await response(response_scope, receive, send)
