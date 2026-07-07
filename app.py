from flask import Flask

from flask_login import LoginManager

from config import Config

from models import (
    db,
    User
)

from routes.predictor import predictor_bp
from routes.college import college_bp
from routes.comparison import comparison_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# -------------------------
# Flask Login Configuration
# -------------------------

login_manager = LoginManager()
login_manager.init_app(app)

# We'll create this route soon
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------
# Register Blueprints
# -------------------------

app.register_blueprint(predictor_bp)
app.register_blueprint(college_bp)
app.register_blueprint(comparison_bp)


if __name__ == "__main__":
    app.run(debug=True)