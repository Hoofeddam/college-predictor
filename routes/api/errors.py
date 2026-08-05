from flask import jsonify


def api_error(code, message, status=400):
    return jsonify({
        "error": {
            "code": code,
            "message": message
        }
    }), status
