from flask import Flask, request, g, render_template
from routes import register_routes
from config import config
from extensions import mysql
from models.entities.modelUser import ModelUser
from utils.jwt_manager import verificar_token

def create_app():
    app = Flask(__name__)
    app.config.from_object(config["dev"])

    mysql.init_app(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    @app.before_request
    def cargar_usuario_actual():
        token = request.cookies.get('access_token')
        g.user = None
        if token:
            user_id = verificar_token(token)
            if user_id:
                g.user = ModelUser.load_user(user_id)

    @app.context_processor
    def inject_user():
        # Inyecta 'user' en el contexto para usar en templates
        return dict(user=g.user)

    register_routes(app)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
