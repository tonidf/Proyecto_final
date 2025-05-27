from .players import players_bp
from .main import main_bp
from .equipos import equipos_bp


def register_routes(app):
    app.register_blueprint(players_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(equipos_bp)