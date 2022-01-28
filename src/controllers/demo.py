from fastapi import APIRouter, Depends, Path, HTTPException, status, Body
from src.dtos.models import CategoryWriteDto, PagingModel, Response, User
from bson.objectid import ObjectId
import src.dependencies as deps

router = APIRouter(prefix="/demo", tags=["Demo"])
service = deps.demo_service()
crypt_service = deps.crypto_service()


@router.get("/")
async def list_categories(paging: PagingModel = Depends()):
    categories = await service.get(paging=paging)
    print(categories)
    return Response(data=categories)


@router.get("/{id}")
async def get_category(id: str = Path(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MongoDB object id")

    category = await service.get(id)

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Object {id} not found")

    return Response(data=category)


# Only allow authorized users to create categories
@router.post("/category")
async def create(model: CategoryWriteDto = Body(...), user: User = Depends(crypt_service)):
    if user.disabled:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, data=None, message="User is disabled")
    id_ = await service.add(model.dict(exclude_unset=True, by_alias=True))
    print(id_)
    return Response(status_code=status.HTTP_201_CREATED, data=id_)


@router.delete("/category/{id}")
async def delete_category(id: str = Path(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MongoDB object id")

    deleted = await service.delete(id)

    return Response(
        status_code=status.HTTP_202_ACCEPTED if deleted else status.HTTP_200_OK,
        data=id,
        message="Deleted" if deleted else "No such object to delete"
    )
