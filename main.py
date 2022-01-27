from fastapi import FastAPI
from src.controllers import health
from config import config

config()

api = FastAPI()
api.include_router(health.router)
