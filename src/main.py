from fastapi import FastAPI
from src.controllers import health, demo, account, user
from src.config import config

api = FastAPI(docs_url="/")
api.include_router(health.router)
api.include_router(demo.router)
api.include_router(account.router)
api.include_router(user.router)


@api.on_event("startup")
def setup():
    config()
