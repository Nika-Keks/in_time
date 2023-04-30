from typing import Tuple

from flask_restx import reqparse

from app import flask_app

pagination_args = reqparse.RequestParser()
pagination_args.add_argument('page', type=int, help='Number of showed page in pagination.')
pagination_args.add_argument('per_page', type=int, help=f'Number of elements per page in pagination. Maximum value '
                                                        f'is {flask_app.config["ITP_ROWS_PER_PAGE"]}')


def get_pagination_args(request_args: dict) -> Tuple[int, int]:
    page = max(1, request_args.get("page", 1, type=int))
    per_page = request_args.get("per_page", flask_app.config['ITP_ROWS_PER_PAGE'], type=int)
    per_page = max(1, min(per_page, flask_app.config['ITP_ROWS_PER_PAGE']))
    return page, per_page
