from typing import List, Optional

from fastapi import Query

from src.dtos.models import Filter


def get_filters(filters: Optional[str] = Query(None)) -> List[Filter]:
    if filters is None:
        return []

    try:
        result: List[Filter] = []
        # filters are separeted by |
        filters_list = filters.split('|')
        for f in filters_list:
            # key and value are separated by :
            key, value = f.split(':')
            if ',' in value:
                result.append(Filter(field=key, value=value.split(',')))
            else:
                result.append(Filter(field=key, value=value))
        return result
    except Exception as e:
        return []
