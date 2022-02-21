from enum import Enum


class NomenclatureType(str, Enum):
    temperature_unit = 'TemperatureUnit'
    data_type = 'DataType'
    type_check_item = 'Type'
    group_check_item = 'Group'
    concept_check_item = 'Concept'
    category_check_item = 'Category'
