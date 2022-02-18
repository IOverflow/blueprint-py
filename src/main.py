from fastapi import FastAPI
from src.controllers import health, demo, account, user
from src.config import config
from fastapi.middleware.cors import CORSMiddleware

origins = ['*']

api = FastAPI(docs_url="/")
api.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'],
                   allow_headers=['*'])
api.include_router(health.router)
api.include_router(account.router)
api.include_router(user.router)


@api.on_event("startup")
def setup():
    config()
