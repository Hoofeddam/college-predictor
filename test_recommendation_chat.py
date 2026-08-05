from app import app

from agents.recommendation_chat_agent import (
    answer_recommendation_question
)

with app.app_context():

    answer = answer_recommendation_question(
        """
        I got AIR 1800 in JEE Advanced under OPEN category.
        I prefer Mechanical Engineering.
        My budget is 15 lakh.
        Recommend the best colleges.
        """
    )

    print(answer)   