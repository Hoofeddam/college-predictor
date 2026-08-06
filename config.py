import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]

    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_MODEL = "gpt-5-mini"

    # -------------------------
    # JWT (API auth, separate from the session-cookie login used by the
    # HTML routes)
    # -------------------------
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]

    # Ensures unhandled exceptions reach our API error handler (returning
    # JSON) instead of Werkzeug's interactive debugger, even with debug=True.
    PROPAGATE_EXCEPTIONS = False
