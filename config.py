from datetime import timedelta


class Config:
    SECRET_KEY = "college_predictor_super_secret_key_2026"

    SQLALCHEMY_DATABASE_URI = (
        "postgresql://flaskuser:StrongPassword123@localhost/college_predictor"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_MODEL = "gpt-5-mini"

    # -------------------------
    # JWT (API auth, separate from the session-cookie login used by the
    # HTML routes)
    # -------------------------
    JWT_SECRET_KEY = "college_predictor_jwt_secret_key_2026"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]