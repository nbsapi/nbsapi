from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from nbsapi.api.dependencies.core import DBSessionDep
from nbsapi.api.v1.routers.adaptationtargets import router as adaptations_router_v1
from nbsapi.api.v1.routers.naturebasedsolutions import router as solutions_router_v1
from nbsapi.api.v1.routers.users import router as users_router_v1
from nbsapi.config import settings
from nbsapi.database import sessionmanager
from nbsapi.utils.auth import create_access_token, is_authenticated

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Load solutions from JSON fixture on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # global solutions
    # json_file_path = os.path.join(os.path.dirname(__file__), "solutions.json")
    # with open(json_file_path, "r") as f:
    #     solutions_data = json.load(f)
    #     solutions = [NatureBasedSolution(**solution) for solution in solutions_data]
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan, title=settings.project_name)


class Token(BaseModel):
    access_token: str
    token_type: str


@app.get("/")
async def root():
    return {"message": "Welcome to nbsapi"}


# @router.get("/solutions/{solution_id}", response_model=NatureBasedSolutionRead)
# async def read_nature_based_solution(solution_id: int, db_session: DBSessionDep):
#     """Retrieve a nature-based solution using its ID"""
#     solution = await get_solution(db_session, solution_id)
#     return solution


@app.post("/auth/token", response_model=Token)
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


# Routers
app.include_router(users_router_v1, prefix="/v1")
app.include_router(solutions_router_v1, prefix="/v1")
app.include_router(adaptations_router_v1, prefix="/v1")


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
