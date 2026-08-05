def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


def serialize_exam(exam):
    return {
        "id": exam.id,
        "name": exam.name
    }


def serialize_category(category):
    return {
        "id": category.id,
        "name": category.name
    }


def serialize_quota(quota):
    return {
        "id": quota.id,
        "name": quota.name
    }


def serialize_college(college):
    return {
        "id": college.id,
        "name": college.name,
        "location": college.location,
        "state": college.state,
        "college_type": college.college_type,
        "fees": college.fees,
        "hostel_fees": college.hostel_fees,
        "nirf_rank": college.nirf_rank,
        "website": college.website
    }


def serialize_branch(branch, include_college=True):
    data = {
        "id": branch.id,
        "branch_name": branch.branch_name,
        "branch_code": branch.branch_code,
        "intake": branch.intake,
        "avg_package": branch.avg_package,
        "median_package": branch.median_package,
        "placement_rate": branch.placement_rate
    }

    if include_college:
        data["college"] = serialize_college(branch.college)

    return data


def serialize_prediction_history(prediction):
    return {
        "id": prediction.id,
        "exam": prediction.exam.name,
        "category": prediction.category.name,
        "quota": prediction.quota.name,
        "rank": prediction.rank,
        "created_at": prediction.created_at.isoformat() if prediction.created_at else None
    }


def serialize_comparison_history(comparison):
    return {
        "id": comparison.id,
        "branch1": serialize_branch(comparison.branch1),
        "branch2": serialize_branch(comparison.branch2),
        "created_at": comparison.created_at.isoformat() if comparison.created_at else None
    }


def serialize_saved_college(saved):
    return {
        "id": saved.id,
        "college": serialize_college(saved.college),
        "created_at": saved.created_at.isoformat() if saved.created_at else None
    }


def serialize_message(message):
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat() if message.created_at else None
    }


def serialize_conversation(conversation, include_messages=False):
    data = {
        "id": conversation.id,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None
    }

    if include_messages:
        data["messages"] = [
            serialize_message(message) for message in conversation.messages
        ]

    return data
