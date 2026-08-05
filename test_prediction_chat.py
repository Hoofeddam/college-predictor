from app import app

from agents.prediction_chat_agent import answer_prediction_question

with app.app_context():

    answer = answer_prediction_question(
        "I got AIR 1200 in JEE Advanced under OPEN category. Which colleges can I get?"
    )

    print(answer)