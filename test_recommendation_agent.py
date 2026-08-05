from app import app

from services.recommendation_service import recommend

with app.app_context():

    result = recommend(
        "JEE Advanced",
        "OPEN",
        "AI",
        1800,
        "Mechanical",
        1500000
    )

    print(result)