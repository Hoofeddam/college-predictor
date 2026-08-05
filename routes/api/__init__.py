from routes.api.auth import api_auth_bp
from routes.api.predictor import api_predictor_bp
from routes.api.comparison import api_comparison_bp
from routes.api.college import api_college_bp
from routes.api.saved import api_saved_bp
from routes.api.profile import api_profile_bp
from routes.api.ai import api_ai_bp


def register_api_blueprints(app):

    app.register_blueprint(api_auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(api_predictor_bp, url_prefix="/api/v1/predictor")
    app.register_blueprint(api_comparison_bp, url_prefix="/api/v1/comparison")
    app.register_blueprint(api_college_bp, url_prefix="/api/v1/colleges")
    app.register_blueprint(api_saved_bp, url_prefix="/api/v1/saved")
    app.register_blueprint(api_profile_bp, url_prefix="/api/v1/profile")
    app.register_blueprint(api_ai_bp, url_prefix="/api/v1/ai")
