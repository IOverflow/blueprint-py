from fastapi import status
from .routers import ApiController

router = ApiController(prefix='/health', tags=['health'])


@router.get('/', status_code=status.HTTP_200_OK)
async def health_check():
    return "Server is alive"
