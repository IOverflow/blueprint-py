from typing import Dict, Any
from bson.objectid import ObjectId

import pytest
from src.dataaccess.repository.repository import RepositoryProtocol
from src.services.service_adapter import CategoryService

# Mock a Category Repository
from src.dtos.models import PagingModel, Category, CategoryWriteDto


class FakeCategoryRepository(RepositoryProtocol):
    def __init__(self):
        self._collection = [
            {"_id": "61f2ca51543a835fd56ec047", "name": "Category 1", "priority": 2,
             "description": "A fantastic category 1"},
            {"_id": "61f2ca51543a835fd56ec048", "name": "Category 2", "priority": 3,
             "description": "A fantastic category 2"},
            {"_id": "61f2ca51543a835fd56ec049", "name": "Category 3", "priority": 8,
             "description": "A fantastic category 3"},
            {"_id": "61f2ca51543a835fd56ec04a", "name": "Category 4", "priority": 1,
             "description": "A fantastic category 4"},
            {"_id": "61f2ca51543a835fd56ec04b", "name": "Category 5", "priority": 6,
             "description": "A fantastic category 5"},
        ]

    async def add(self, entity: Dict[str, Any]):
        entity['_id'] = str(ObjectId())
        self._collection.append(entity)
        return entity['_id']

    async def get(self, id: str):
        for d in self._collection:
            if d['_id'] == id:
                return Category(**d)
        else:
            return None

    async def delete(self, id: str) -> bool:
        for d in self._collection:
            if d['_id'] == id:
                self._collection.remove(d)
                return True
        else:
            return False

    async def get_all(self, paging: PagingModel):
        return list(map(lambda d: Category(**d), self._collection))

    async def update(self, id: str, entity: Dict[str, Any]) -> bool:
        for d in self._collection:
            if d['_id'] == id:
                d.update(entity)
                return True
        else:
            return False


@pytest.fixture
def category_service():
    return CategoryService(FakeCategoryRepository())


@pytest.mark.asyncio
async def test_demo_category_service_adds_category(category_service):
    new_entity = CategoryWriteDto(name="Category6", priority=11)
    response = await category_service.add(new_entity.dict(exclude_unset=True, by_alias=True))
    assert ObjectId.is_valid(response)
    assert len(category_service._repo._collection) == 6


@pytest.mark.asyncio
async def test_demo_category_service_lists(category_service):
    categories = await category_service.get()
    assert len(categories) == 5
    assert all(isinstance(x, Category) for x in categories)


@pytest.mark.asyncio
async def test_demo_category_service_show_category(category_service):
    category = await category_service.get("61f2ca51543a835fd56ec049")
    assert isinstance(category, Category)
    assert category.id == ObjectId("61f2ca51543a835fd56ec049")
    assert category.name == "Category 3"


@pytest.mark.asyncio
async def test_demo_category_service_update(category_service):
    updated = await category_service.update("61f2ca51543a835fd56ec049", {"name": "Updated"})
    assert updated
    assert category_service._repo._collection[2]["name"] == "Updated"
