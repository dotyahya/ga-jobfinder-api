from fastapi import FastAPI
from backend.routers import jobfinder, health

app = FastAPI()

app.include_router(health.router)
app.include_router(jobfinder.router, prefix="/jobfinder", tags=["jobfinder"])