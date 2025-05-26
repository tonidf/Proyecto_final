from .players import players_bp
from .main import main_bp


def register_routes(app):
    app.register_blueprint(players_bp)
    app.register_blueprint(main_bp)