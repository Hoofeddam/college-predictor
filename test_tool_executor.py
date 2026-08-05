from app import app
from tools.college_compare import compare_colleges

with app.app_context():

    result = compare_colleges(
        "IIT Bombay",
        "CSE",
        "IIT Delhi",
        "CSE"
    )

    print(result)