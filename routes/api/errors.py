from flask import jsonify, request, current_app
from werkzeug.exceptions import HTTPException

API_PATH_PREFIX = "/api/"


def api_error(code, message, status=400):
    return jsonify({
        "error": {
            "code": code,
            "message": message
        }
    }), status


def _is_api_request():
    return request.path.startswith(API_PATH_PREFIX)


def register_api_error_handlers(app, jwt):
    """Makes every /api/* response -- expected or not -- use the same
    {"error": {"code", "message"}} envelope: routing errors (404/405),
    unexpected exceptions, and flask-jwt-extended's own auth failures
    (which otherwise return a differently-shaped {"msg": ...} body).
    Non-API routes are left to Flask's normal HTML error handling.
    """

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):

        if not _is_api_request():
            return error

        code = (error.name or "http_error").lower().replace(" ", "_")
        return api_error(code, error.description or error.name, error.code)

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):

        if not _is_api_request():
            raise error

        current_app.logger.exception("Unhandled API error")
        return api_error(
            "internal_error",
            "Something went wrong. Please try again.",
            500
        )

    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        return api_error("missing_token", reason, 401)

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        return api_error("invalid_token", reason, 422)

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return api_error("token_expired", "The token has expired.", 401)
