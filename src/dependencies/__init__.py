from typing import Optional

from fastapi import Query

from src.dtos.models import PyObjectId, Nomenclature, User


def get_filters(filters: Optional[str] = Query(None)) -> dict:
    if filters is None:
        return dict()

    try:
        result = dict()
        # filters are separeted by |
        filters_list = filters.split('|')
        for f in filters_list:
            # key and value are separated by :
            key, value = f.split(':')
            if ',' in value:
                result[key] = value.split(',')
            else:
                result[key] = value
        return result
    except Exception as e:
        return dict()


async def get_nomenclature(id: PyObjectId):
    return await Nomenclature.get(id)


async def get_user_from_request(id: PyObjectId):
    return await User.get(id)
