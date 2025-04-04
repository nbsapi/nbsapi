from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.api.v1.routers.adaptationtargets import router as adaptations_router_v1
from nbsapi.api.v1.routers.impacts import router as impacts_router_v1
from nbsapi.api.v1.routers.naturebasedsolutions import router as solutions_router_v1
from nbsapi.api.v1.routers.users import router as users_router_v1
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


description = """
## NBSAPI
An API for interoperability between digital tools that help to build and manage nature-based solutions in the built and natural environment. This API provides a way for tool builders to share their data with interested parties in a standardized fashion. The API is fully configurable in that the tool builders customize the data sharing based on the capability of their service. 


The API provides endpoints for these operations and in general we anticipate that the NbS tool / service owner will be using the POST endpoints to populate the service description and the clients will primarily use the GET endpoints to query and process the data. As the API grows, this pattern may change. 

The API also provides a way to authenticate and authorize via JWT tokens, it is expected that the tool / service builder (NBSAPI adopter) will specify their own access method and other rules, we anticipate that for some of the portions of the API there may be access controls and limitations. An example is defined in the `Users` endpoint here, this can be swapped with any other token generation mechanism that the adopter may have. 

Definitions of some key concepts are below: 

### Nature Based Solutions
Solutions that are inspired and supported by nature, which are cost-effective, **simultaneously provide environmental, social and economic benefits** and **help build resilience**.  
Such solutions bring more, and more diverse, nature and natural features and processes into cities, landscapes and seascapes, through **locally adapted, resource-efficient and systemic interventions**.
Your service handles and manages these solutions internally, the `solutions` endpoints provide a way for your to share your tool or service's capabilities via these endpoints. You use the "Add solutions" endpoint once to publish your tool or services's capabilities.

### Adaptation Targets
Adaptation targets define and quantify the type of adaptation facilitated by a `Nature-Based Solution`, each target having an associated value 0 - 100.  
Each NbS may have **one or more** adaptation targets. As a tool builder, you specify the adaptation target for your service. 

### Impacts
These are the adaptation impacts of `Nature-Based Solution`s. An impact has a magnitude, an `ImpactIntensity`, and an associated `ImpactUnit`, which may describe e.g. area or volume.

"""

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "solutions",
        "description": "Retrieve and create Nature-Based Solutions.",
    },
    {
        "name": "adaptation targets",
        "description": "Retrieve and create Adaptation Targets.",
    },
    {
        "name": "impacts",
        "description": "Retrieve adaptation impacts.",
    },
]

app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description=description,
    openapi_tags=tags_metadata,
)


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
    return Token(access_token=access_token, token_type="bearer")


@app.get("/currentversion", response_model=ApiVersion)
async def get_current_api_version(db_session: DBSessionDep):
    """Retrieve the current API version"""
    cv = await get_current_version(db_session)
    return cv


@app.get("/contact", response_model=Contact)
async def get_contact(db_session: DBSessionDep):
    """Retrieve the contact address for this API"""
    return Contact(
        website=settings.contact_website
    )


# Routers
app.include_router(users_router_v1, prefix="/v1")
app.include_router(solutions_router_v1, prefix="/v1")
app.include_router(adaptations_router_v1, prefix="/v1")
app.include_router(impacts_router_v1, prefix="/v1")
# ensure that the route below is added AFTER all other routes
app.mount("/", StaticFiles(directory="html", html=True), name="index")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True, port=8000)
