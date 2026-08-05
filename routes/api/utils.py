from flask_jwt_extended import get_jwt_identity

from models import User


def current_api_user():
    user_id = get_jwt_identity()

    if user_id is None:
        return None

    return User.query.get(int(user_id))
