from flask import Blueprint, request, jsonify

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from models import db, User
from services.serializers import serialize_user
from routes.api.errors import api_error
from routes.api.utils import current_api_user

api_auth_bp = Blueprint("api_auth", __name__)


@api_auth_bp.route("/signup", methods=["POST"])
def signup():

    data = request.get_json(silent=True) or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return api_error(
            "missing_fields",
            "username, email and password are required.",
            400
        )

    if User.query.filter_by(email=email).first():
        return api_error("email_taken", "Email already exists.", 409)

    if User.query.filter_by(username=username).first():
        return api_error("username_taken", "Username already exists.", 409)

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"user": serialize_user(user)}), 201


@api_auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return api_error(
            "missing_fields",
            "email and password are required.",
            400
        )

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return api_error(
            "invalid_credentials",
            "Invalid email or password.",
            401
        )

    identity = str(user.id)

    return jsonify({
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
        "user": serialize_user(user)
    })


@api_auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    access_token = create_access_token(identity=get_jwt_identity())

    return jsonify({"access_token": access_token})


@api_auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():

    user = current_api_user()

    if not user:
        return api_error("not_found", "User not found.", 404)

    return jsonify({"user": serialize_user(user)})
