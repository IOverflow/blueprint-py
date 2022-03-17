from re import finditer
from typing import List, Optional

from fastapi import Path, Security, Body, Depends, status

from src.dependencies import get_filters
from src.services.service_adapter import PagingModel, NomenclaturesService
from src.dtos.viewmodels import (Response, NomenclatureForm, Page, NomenclatureViewModel,
                                 NomenclatureTypeViewModel)
from src.dtos.models import User, Filter
from src.services.crypto import adminRole, anyRole
from src.inmutables import NomenclatureType
from .routers import ApiController

router = ApiController(prefix='/nomenclature', tags=['Nomenclature'])
service = NomenclaturesService()


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


@router.get('', response_model=Response[Page[NomenclatureViewModel]])
async def get_all_nomenclatures(
        user: User = Security(adminRole, scopes=['nomenclature:read']),
        paging: PagingModel = Depends(),
        filters: Optional[List[Filter]] = Depends(get_filters)
):
    """
    Returns all nomenclatures defined on the system.
    This endpoint requires the Admin role and 'nomenclature:read'
    permission
    """
    nomenclatures = await service.get(paging=paging, filters=filters)
    total = await service.count(filters)
    return Response(data=Page(items=nomenclatures, total=total, records=len(nomenclatures)))


@router.get('/types', response_model=Response[List[NomenclatureTypeViewModel]])
def get_all_nomenclature_types():
    """
    This endpoints does not enforce a specific role or
    user permission, neither required an authenticated
    user for the moment. This could change in the future.
    Access this endpoint to retrieves a list of all the
    nomenclature types available (namely, all values of the
    NomenclatureType Enum)
    """
    return Response(
        data=list({"value": e.value,
                   "label": " ".join(camel_case_split(e.value)),
                   "has_level": e == NomenclatureType.type_check_item,
                   "has_pattern": e == NomenclatureType.data_type
                   } for e in NomenclatureType))


@router.get('/{id}', response_model=Response[NomenclatureViewModel])
async def get_nomenclature_by_id(
        user: User = Security(adminRole, scopes=['nomenclature:read']),
        id: str = Path(...)
):
    """
    Returns al the details of a nomenclature. This is useful for
    populating a form for editing the nomenclature.
    Requires an Admin role and 'nomenclature:read' permissions.
    """
    nomenclature = await service.get(id=id)
    if nomenclature is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND, message="Nomenclature not found")

    return Response(data=nomenclature)


@router.get('/type/{nomenclature_type}', response_model=Response[Page[NomenclatureViewModel]])
async def get_nomenclatures_by_type(
        user: User = Security(anyRole, scopes=['nomenclature:read']),
        nomenclature_type: NomenclatureType = Path(...)
):
    """
    Gets all nomenclatures that belongs to a specific type.
    This is useful for populating select boxes on entities
    that depends on a given nomenclature.
    Requires 'nomenclature:read' permission.
    """
    nomenclatures = await service.get_nomenclatures_by_type(nomenclature_type)
    total = await service.count([Filter(field='type', value='nomenclature_type')])
    return Response(
        data=Page(items=nomenclatures, records=len(nomenclatures), total=total)
    )


@router.delete('/{id}', response_model=Response[str])
async def delete_nomenclature(
        user: User = Security(adminRole, scopes=['nomenclature:delete']),
        id: str = Path(...)
):
    """
    Deletes a nomenclature from the system. It requires "users:delete" permission
    and an admin Role
    """
    if await service.delete(id):
        return Response(message="Delete successfully", data=id, status_code=status.HTTP_202_ACCEPTED)

    return Response(message="Nomenclature could not been deleted", status_code=status.HTTP_400_BAD_REQUEST)


@router.post('', response_model=Response[NomenclatureViewModel])
async def create_nomenclature(
        user: User = Security(adminRole, scopes=['nomenclature:write']),
        model: NomenclatureForm = Body(...)
):
    """
    Creates a new nomenclature and returns the new object.
    Requires Admin role and 'nomenclature:write' permission.
    """
    data = model.dict()
    _id = await service.add(data)

    return Response(data=await service.get(id=_id))


@router.put('/{id}', response_model=Response[NomenclatureViewModel])
async def update_nomenclature(
        user: User = Security(adminRole, scopes=['nomenclature:write']),
        id: str = Path(...),
        model: NomenclatureForm = Body(...)
):
    """
    Updates the data collected in model to the Nomenclature
    represented by id. Requires Admin role and nomenclature:write permission
    """
    data = model.dict(exclude_unset=True)
    if await service.update(id, data):
        new_nomenclature = await service.get(id=id)
        return Response(status_code=status.HTTP_201_CREATED, data=new_nomenclature)
