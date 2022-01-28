from fastapi import FastAPI
from src.controllers import health, demo, account
from src.config import config

api = FastAPI()
api.include_router(health.router)
api.include_router(demo.router)
api.include_router(account.router)


@api.on_event("startup")
def setup():
    config()
