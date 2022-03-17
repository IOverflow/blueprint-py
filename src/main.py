from beanie import init_beanie
from fastapi import FastAPI
from src.controllers import health, account, user, nomenclature
from src.config import config
from fastapi.middleware.cors import CORSMiddleware

origins = ['*']

api = FastAPI(docs_url="/api/v1/admin/swag-docs",
              redoc_url='/api/v1/admin/docs',
              openapi_url='/api/v1/admin/openapi.json',
              title="Admin Project API",
              version="0.1.0",
              contact={
                  'name': "NextX Team"
              })
api.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'],
                   allow_headers=['*'])
api.include_router(health.router, prefix='/api/v1/admin')
api.include_router(account.router, prefix='/api/v1/admin')
api.include_router(user.router, prefix='/api/v1/admin')
api.include_router(nomenclature.router, prefix='/api/v1/admin')


@api.on_event("startup")
async def setup():
    config()
    from src.dataaccess.database import db
    from src.dtos.models import User
    from src.dtos.models import Nomenclature
    await init_beanie(db, document_models=[
        User,
        Nomenclature
    ])
