from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from decouple import config

database_url = config("DEVELOPMENT_DATABASE_URL")
database = config("DEVELOPMENT_DATABASE")

motor_client: AsyncIOMotorClient = AsyncIOMotorClient(database_url)
db: AsyncIOMotorDatabase = motor_client[database]
