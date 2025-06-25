from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nbsapi.api.dependencies.versioning import (
    ApiVersion as ApiVersionEnum,
    get_api_version,
    VersionNegotiationMiddleware,
)
from nbsapi.api.docs import create_docs_router

from nbsapi.api.dependencies.core import DBSessionDep

# v1 API routers
from nbsapi.api.v1.routers.adaptationtargets import router as adaptations_router_v1
from nbsapi.api.v1.routers.impacts import router as impacts_router_v1
from nbsapi.api.v1.routers.naturebasedsolutions import router as solutions_router_v1
from nbsapi.api.v1.routers.users import router as users_router_v1

# v2 API routers
from nbsapi.api.v2.routers.naturebasedsolutions import router as solutions_router_v2
from nbsapi.api.v2.routers.impacts import router as impacts_router_v2
from nbsapi.api.v2.routers.projects import router as projects_router_v2
from nbsapi.api.v2.routers.measure_types import router as measure_types_router_v2
from nbsapi.config import settings
from nbsapi.crud.apiversion import get_current_version
from nbsapi.database import sessionmanager
from nbsapi.schemas.apiversion import ApiVersion
from nbsapi.schemas.contact import Contact
from nbsapi.utils.auth import create_access_token, is_authenticated

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Load solutions from JSON fixture on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "solutions",
        "description": "Retrieve and create Nature-Based Solutions with GeoJSON geometry, styling, and physical properties.",
    },
    {
        "name": "impacts",
        "description": "Impact management with specialized types (climate, water quality, cost) for quantitative measurements.",
    },
    {
        "name": "projects",
        "description": "Group multiple Nature-Based Solutions with shared settings, targets, and spatial contexts.",
    },
    {
        "name": "measure types",
        "description": "Predefined solution types (rain gardens, bioswales, etc.) with default properties.",
    },
]

app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    openapi_tags=tags_metadata,
    # Disable default docs - we'll use our custom versioned docs
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


# API version info endpoint
@app.get("/api/version")
async def get_api_version_info(
    request: Request, api_version: ApiVersionEnum = Depends(get_api_version)
):
    """Get information about the current API version"""
    return {
        "version": api_version,
        "latest": ApiVersionEnum.V2,
        "current": api_version,
        "deprecated": api_version == ApiVersionEnum.V1,
        "available_versions": [v.value for v in ApiVersionEnum],
    }


class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/auth/token", response_model=Token, tags=["users"])
async def login_for_access_token(
    db_session: DBSessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await is_authenticated(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")  # noqa: S106


@app.get("/currentversion", response_model=ApiVersion)
async def get_current_api_version(db_session: DBSessionDep):
    """Retrieve the current API version"""
    cv = await get_current_version(db_session)
    return cv


@app.get("/contact", response_model=Contact)
async def get_contact(db_session: DBSessionDep):
    """Retrieve the contact address for this API"""
    return Contact(website=settings.contact_website)


# Add custom docs router for versioned API documentation
app.include_router(create_docs_router())

# Routers
# v1 API
app.include_router(users_router_v1, prefix="/v1")
app.include_router(solutions_router_v1, prefix="/v1")
app.include_router(adaptations_router_v1, prefix="/v1")
app.include_router(impacts_router_v1, prefix="/v1")

# v2 API
app.include_router(solutions_router_v2, prefix="/v2")
app.include_router(impacts_router_v2, prefix="/v2")
app.include_router(projects_router_v2, prefix="/v2")
app.include_router(measure_types_router_v2, prefix="/v2")

# ensure that the route below is added AFTER all other routes
app.mount("/", StaticFiles(directory="html", html=True), name="index")


origins = ["*"]

# Add middleware for version negotiation
app.add_middleware(VersionNegotiationMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True, port=8000)
