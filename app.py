from flask import Flask

from flask_login import LoginManager
from flask_jwt_extended import JWTManager

from config import Config

from models import (
    db,
    User
)

from routes.predictor import predictor_bp
from routes.college import college_bp
from routes.comparison import comparison_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.saved import saved_bp
from routes.profile import profile_bp
from routes.ai import ai_bp

from routes.api import register_api_blueprints
from routes.api.errors import register_api_error_handlers

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# -------------------------
# Flask Login Configuration (session-cookie auth for the HTML routes)
# -------------------------

login_manager = LoginManager()
login_manager.init_app(app)

# We'll create this route soon
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------
# JWT Configuration (token auth for the /api/v1 routes)
# -------------------------

jwt = JWTManager(app)

register_api_error_handlers(app, jwt)


# -------------------------
# Register Blueprints
# -------------------------

app.register_blueprint(predictor_bp)
app.register_blueprint(college_bp)
app.register_blueprint(comparison_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(saved_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(ai_bp)

register_api_blueprints(app)


if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )