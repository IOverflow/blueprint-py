from typing import Protocol, Dict, Any, Optional
from abc import abstractmethod
from motor.motor_asyncio import AsyncIOMotorCollection
from src.dataaccess.database import db
from src.dtos.models import Category, PagingModel
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


class CategoryRepository:

    def __init__(self, database=db, table_name="categories"):
        self._collection: AsyncIOMotorCollection = database[table_name]

    async def get(self, id: str) -> Optional[Category]:
        if (category := await self._collection.find_one({"_id": ObjectId(id)})) is not None:
            return Category(**category)
        return None

    async def delete(self, id: str) -> bool:
        delete_result = await self._collection.delete_one({'_id': ObjectId(id)})
        return delete_result.deleted_count == 1

    async def get_all(self, paging: PagingModel):
        objects = await self._collection.find(limit=paging.limit, skip=paging.skip).to_list(paging.limit)
        return list(map(lambda d: Category(**d), objects))

    async def update(self, id: str, entity: Dict[str, Any]) -> bool:
        update_result = await self._collection.update_one({"_id": ObjectId(id)}, {"$set": entity})
        return update_result.modified_count == 1

    async def add(self, entity: Dict[str, Any]) -> str:
        created_category = await self._collection.insert_one(entity)
        print(created_category.inserted_id)
        return created_category.inserted_id
