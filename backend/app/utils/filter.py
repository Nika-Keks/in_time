from distutils.util import strtobool
from typing import Optional

from flask_sqlalchemy import Model
from sqlalchemy import String, cast, func
from sqlalchemy.sql.elements import BinaryExpression, and_

FILTERING_OPERATORS = {
    "eq": "__eq__",
    "not": "__ne__",
    "gte": "__ge__",
    "lte": "__le__",
    "gt": "__gt__",
    "lt": "__lt__",
}
supported_operators = [*list(FILTERING_OPERATORS.keys()), "isnull"]


def parse_filter_operation(
    model: Model, field: str, value: str, op: str
) -> BinaryExpression:
    column = getattr(model, field)

    str_column = func.lower(cast(column, String))
    str_value = func.lower(value)

    if op == "isnull":
        usable_operator = "is_" if strtobool(value) else "isnot"
        str_value = None
    else:
        usable_operator = FILTERING_OPERATORS.get(op, "__eq__")
    return getattr(str_column, usable_operator)(str_value)


def parse_filters_data(model: Model, filters: list) -> Optional[BinaryExpression]:
    if len(filters) == 0:
        return None

    result_operation = parse_filter_operation(model, **(filters[0]))
    for filter_info in filters[1:]:
        result_operation = and_(result_operation, parse_filter_operation(model, **filter_info))

    return result_operation


def parse_ordering_criteria(model: Model, field: str, desc: bool) -> BinaryExpression:
    column = getattr(model, field)
    return getattr(column, "desc")() if desc else column
