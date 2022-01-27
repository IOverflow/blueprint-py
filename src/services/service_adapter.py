from typing import Dict, Any, Optional, Union, List
from fastapi import HTTPException, status, Depends
from src.dataaccess.repository.repository import RepositoryProtocol, CategoryRepository
from src.dtos.models import Entity, PagingModel


class BaseService:
    def __init__(self, repo: RepositoryProtocol):
        self._repo = repo

    async def add(self, model: Dict[str, Any]) -> str:
        object_id = await self._repo.add(model)
        return object_id

    async def delete(self, id: str) -> bool:
        success = await self._repo.delete(id)
        return success

    async def get(self, id: Optional[str] = None, paging=PagingModel()) -> Union[Entity, List[Entity]]:
        if id:
            object_response = await self._repo.get(id)
        else:
            object_response = await self._repo.get_all(paging)
        return object_response

    async def update(self, id: str, model=None) -> bool:
        if model is None:
            model = dict()
        if len(model) >= 1:
            updated = await self._repo.update(id, model)
            return updated

        if await self._repo.get(id) is not None:
            return False

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Object {id} not found")


class CategoryService(BaseService):
    def __init__(self, repo: CategoryRepository = Depends()):
        super(CategoryService, self).__init__(repo)
