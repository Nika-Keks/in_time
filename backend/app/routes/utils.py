import json
from typing import Tuple

from flask_restx import reqparse, fields
from flask_sqlalchemy.model import Model

from app import flask_app, api
from app.utils.filter import parse_filters_data, supported_operators, parse_ordering_criteria

pagination_args = reqparse.RequestParser()
pagination_args.add_argument('page', type=int, help='Number of showed page in pagination.')
pagination_args.add_argument('per_page', type=int, help=f'Number of elements per page in pagination. Maximum value '
                                                        f'is {flask_app.config["ITP_ROWS_PER_PAGE"]}')


def get_pagination_args(request_args: dict) -> Tuple[int, int]:
    page = max(1, request_args.get("page", 1, type=int))
    per_page = request_args.get("per_page", flask_app.config['ITP_ROWS_PER_PAGE'], type=int)
    per_page = max(1, min(per_page, flask_app.config['ITP_ROWS_PER_PAGE']))
    return page, per_page


filter_input = api.model('filter', {
    'field': fields.String,
    'op': fields.String(enum=supported_operators),
    'value': fields.String,
})
order_arg = api.model('order_by', {
    'field': fields.String,
    'desc': fields.Boolean,
})

filter_args = reqparse.RequestParser()
filter_args.add_argument('filters', type=str, help='List of filters to apply')
filter_args.add_argument('orderBy', type=str, help='List of fields ordering')


def get_filter_order_query(request_args: dict, model: Model):
    filters_data = json.loads(request_args.get("filters", "[]"))
    ordering = json.loads(request_args.get("orderBy", "[]"))

    filters = parse_filters_data(model, filters_data)
    orderBy = [parse_ordering_criteria(model, **order_info) for order_info in ordering]

    query = getattr(model, "query")
    if filters is not None:
        query = query.filter(filters)
    if len(orderBy) > 0:
        query = query.order_by(*orderBy)
    return query
