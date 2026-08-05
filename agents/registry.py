from agents.prediction_chat_agent import (
    answer_prediction_question
)
from agents.prediction_extractor import (
    extract_prediction_details
)

from agents.comparison_chat_agent import (
    answer_comparison_question
)
from agents.comparison_extractor import (
    extract_comparison_details
)

from agents.recommendation_chat_agent import (
    answer_recommendation_question
)
from agents.recommendation_extractor import (
    extract_recommendation_details
)


AGENTS = {

    "prediction": {

        "description": """
Predict colleges based on a student's rank.
Check cutoff eligibility.
Find colleges a student can get using exam, category, quota and rank.
""",

        "collects_information": True,

        "required_fields": [
            "exam",
            "rank",
            "category",
            "quota"
        ],

        "extractor": extract_prediction_details,

        "handler": answer_prediction_question
    },

    "comparison": {

        "description": """
Compare two colleges or branches.
Compare placements, fees, hostel fees, NIRF rankings and cutoffs.
""",

        "collects_information": True,

        "required_fields": [
            "college_1",
            "branch_1",
            "college_2",
            "branch_2"
        ],

        "extractor": extract_comparison_details,

        "handler": answer_comparison_question
    },

    "recommendation": {

        "description": """
Recommend colleges based on user preferences,
budget, preferred branch and academic profile.
Use this when the user wants suggestions instead of eligibility checking.
""",

        "collects_information": True,

        "required_fields": [
            "exam",
            "rank",
            "category",
            "quota"
        ],

        "extractor": extract_recommendation_details,

        "handler": answer_recommendation_question
    },

    "knowledge": {

        "description": """
Answer general engineering admission questions.
Explain JEE, JoSAA, CSAB, branches,
placements, careers and counselling.
""",

        "collects_information": False,

        "required_fields": [],

        "extractor": None,

        "handler": None
    }

}