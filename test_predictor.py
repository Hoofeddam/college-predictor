from app import app
from services.prediction_service import search_colleges

with app.app_context():

    result = search_colleges(
        "JEE Advanced",
        "OPEN",
        "AI",
        1200
    )

    print(result)