from typing import Protocol, Dict, Any, Optional
from abc import abstractmethod
from motor.motor_asyncio import AsyncIOMotorCollection
from src.dataaccess.database import db
from src.dtos.models import Category, PagingModel, User
from bson.objectid import ObjectId


class RepositoryProtocol(Protocol):
    @abstractmethod
    async def add(self, entity: Dict[str, Any]):
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: str):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, paging: PagingModel):
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: str, entity: Dict[str, Any]) -> bool:
        raise NotImplementedError


class BaseRepository:
    def __init__(self, table_name, schema: type, database=db):
        self._collection: AsyncIOMotorCollection = database[table_name]
        self._schema = schema

    async def get(self, id: str) -> Optional[Category]:
        if (obj := await self._collection.find_one({"_id": ObjectId(id)})) is not None:
            return self._schema(**obj)
        return None

    async def delete(self, id: str) -> bool:
        delete_result = await self._collection.delete_one({'_id': ObjectId(id)})
        return delete_result.deleted_count == 1

    async def get_all(self, paging: PagingModel):
        objects = await self._collection.find(limit=paging.limit, skip=paging.skip).to_list(paging.limit)
        return list(map(lambda d: self._schema(**d), objects))

    async def update(self, id: str, entity: Dict[str, Any]) -> bool:
        result = await self._collection.update_one({"_id": ObjectId(id)}, {"$set": entity})
        return result.modified_count == 1

    async def add(self, entity: Dict[str, Any]) -> str:
        created_obj = await self._collection.insert_one(entity)
        return created_obj.inserted_id


class CategoryRepository(BaseRepository):

    def __init__(self, database=db, schema=Category, table_name="categories"):
        super().__init__(table_name, schema, database)


# ===========================================    USER REPOSITORY   =================================
class UserRepository(BaseRepository):
    def __init__(self, table_name="users", schema=User, database=db):
        super().__init__(table_name, schema, database)

    async def get_by_username(self, username):
        if (user_data := await self._collection.find_one({'username': username})) is not None:
            return User(**user_data)

        return None

# ==================================================================================================
