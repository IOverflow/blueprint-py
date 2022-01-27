from fastapi import FastAPI
from src.controllers import health


api = FastAPI()
api.include_router(health.router)
