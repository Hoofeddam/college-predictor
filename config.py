class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://flaskuser:StrongPassword123@localhost/college_predictor"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False