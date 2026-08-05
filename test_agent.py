from app import app
from agent.agent import run_agent

with app.app_context():

    response = run_agent(
        "Recommend good CSE colleges under 15 lakh for JEE Advanced OPEN AI rank 500."
    )

    print(response)