from services.prediction_service import search_colleges


def recommend(
    exam,
    category,
    quota,
    rank,
    preferred_branch=None,
    budget=None
):

    prediction = search_colleges(
        exam,
        category,
        quota,
        rank
    )

    colleges = prediction["results"]

    recommended = colleges

    if budget is not None:

        recommended = [
            college
            for college in recommended
            if college["fees"] <= budget
        ]

    if preferred_branch:

        preferred = [
            college
            for college in recommended
            if preferred_branch.lower()
            in college["branch"].lower()
        ]

        if preferred:
            recommended = preferred

    return recommended