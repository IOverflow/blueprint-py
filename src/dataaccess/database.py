import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


database_url = os.getenv("DEVELOPMENT_DATABASE_URL")
database = os.getenv("DEVELOPMENT_DATABASE")

motor_client: AsyncIOMotorClient = AsyncIOMotorClient(database_url)
db: AsyncIOMotorDatabase = motor_client[database]
