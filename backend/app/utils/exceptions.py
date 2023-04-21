from flask import jsonify

from app import flask_app

ok = 200
created = 201


class ITPError(Exception):
    pass


class ITPAuthError(ITPError):
    code = 401
    description = "Unauthorized"


class ITPForbiddenError(ITPError):
    code = 403
    description = "Request forbidden Error"


class ITPInvalidError(ITPError):
    code = 400
    description = "Update Error"


class ITPNotFound(ITPError):
    code = 404
    description = "Not found error"


class ITPNotModified(ITPError):
    code = 304
    description = "Not modified session"


@flask_app.errorhandler(ITPError)
def handle_exception(err):
    response = {"error": err.description, "message": ""}
    if len(err.args) > 0:
        response["message"] = err.args[0]
    flask_app.logger.error(f"{err.description}: {response['message']}")
    return jsonify(response), err.code
