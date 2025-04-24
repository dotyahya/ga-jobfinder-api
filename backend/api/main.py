from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import jobfinder, health

app = FastAPI()

# cors settings to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(jobfinder.router, prefix="/jobfinder", tags=["jobfinder"])