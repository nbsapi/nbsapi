from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from nbsapi.api.v1.routers.adaptationtargets import router as adaptations_router_v1
from nbsapi.api.v1.routers.naturebasedsolutions import router as solutions_router_v1
from nbsapi.config import settings
from nbsapi.database import sessionmanager


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

app.mount("/", StaticFiles(directory="html", html=True), name="index")


# Routers
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
