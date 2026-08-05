from flask import Blueprint, jsonify

from models import College
from services.serializers import serialize_college, serialize_branch
from routes.api.errors import api_error

api_college_bp = Blueprint("api_college", __name__)


@api_college_bp.route("/<int:college_id>", methods=["GET"])
def college_details(college_id):

    college = College.query.get(college_id)

    if not college:
        return api_error("not_found", "College not found.", 404)

    data = serialize_college(college)
    data["branches"] = [
        serialize_branch(branch, include_college=False)
        for branch in college.branches
    ]

    return jsonify({"college": data})
