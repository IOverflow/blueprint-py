from fastapi import APIRouter, Path, Security, Body, Query, Depends, status
from src.services.service_adapter import PagingModel, NomenclaturesService
from src.dtos.viewmodels import (NomenclaturesResponseViewModel, NomenclatureTypesViewModel,
                                 NomenclatureResponseViewModel, Response)
from src.dtos.models import User
from src.services.crypto import adminRole, anyRole
from src.inmutables import NomenclatureType

router = APIRouter(prefix='nomenclature', tags=['Nomenclature'])
service = NomenclaturesService()


@router.get('', response_model=NomenclaturesResponseViewModel)
async def get_all_nomenclatures(
        user: User = Security(adminRole, scopes=['nomenclature:read']),
        paging: PagingModel = Depends()
):
    """
    Returns all nomenclatures defined on the system.
    This endpoint requires the Admin role and 'nomenclature:read'
    permission
    """
    nomenclatures = await service.get(paging=paging)
    return NomenclaturesResponseViewModel(data=nomenclatures)


@router.get('/types', response_model=NomenclatureTypesViewModel)
async def get_all_nomenclature_types():
    """
    This endpoints does not enforce a specific role or
    user permission, neither required an authenticated
    user for the moment. This could change in the future.
    Access this endpoint to retrieves a list of all the
    nomenclature types available (namely, all values of the
    NomenclatureType Enum)
    """
    return NomenclatureTypesViewModel(data=list(e.value for e in NomenclatureType))


@router.get('/{id}', response_model=NomenclatureResponseViewModel)
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
        return NomenclatureResponseViewModel(status_code=status.HTTP_404_NOT_FOUND, message="Nomenclature not found")

    return NomenclatureTypesViewModel(data=nomenclature)


@router.delete('/{id}', response_model=Response)
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

    return Response(message="Nomenclature could not been deleted", status=status.HTTP_400_BAD_REQUEST)


@router.get('/{nomenclature_type}', response_model=NomenclaturesResponseViewModel)
async def get_nomenclatures_by_type(
        user: User = Security(adminRole, scopes=['nomenclature:read']),
        nomenclature_type: NomenclatureType = Path(...)
):
    """
    Gets all nomenclatures that belongs to a specific type.
    This is useful for populating select boxes on entities
    that depends on a given nomenclature.
    Requires 'nomenclature:read' permission and Admin role.
    """
    nomenclatures = await service.get_nomenclatures_by_type(nomenclature_type)
    return NomenclaturesResponseViewModel(data=nomenclatures)
