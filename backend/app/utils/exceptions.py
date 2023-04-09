from flask import jsonify

from app import flask_app


class ITPError(Exception):
    pass


class ITPAuthError(ITPError):
    code = 403
    description = "Authentication Error"


class ITPForbiddenError(ITPError):
    code = 404
    description = "Request forbidden Error"


class ITPUpdateError(ITPError):
    code = 402 # TODO: set code for wrong arguments
    description = "Update Error"


class ITPNotFound(ITPError):
    code = 401
    description = "Not found error"


@flask_app.errorhandler(ITPError)
def handle_exception(err):
    response = {"error": err.description, "message": ""}
    if len(err.args) > 0:
        response["message"] = err.args[0]
    flask_app.logger.error(f"{err.description}: {response['message']}")
    return jsonify(response), err.code
