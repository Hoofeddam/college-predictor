from app import app

from agents.comparison_chat_agent import answer_comparison_question

with app.app_context():

    answer = answer_comparison_question(
        "Compare IIT Bombay Computer Science and IIT Delhi Electrical Engineering"
    )

    print(answer)