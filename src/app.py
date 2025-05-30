from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from routes import register_routes  # Añadir "scr." delante del from para ejecutar el script de insertar_equipos.py
from config import config # Añadir "scr." delante del from para ejecutar el script de insertar_equipos.py
from extensions import mysql, login_manager # Añadir "scr." delante del from para ejecutar el script de insertar_equipos.py
from .models.entities.modelUser import ModelUser  # Importar el modelo de usuario
from flask_login import LoginManager


def create_app():
    app = Flask(__name__)
    app.config.from_object(config["dev"])

    mysql.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'  # Define la vista de inicio de sesión

    @login_manager.user_loader
    def load_user(user_id):
        return ModelUser.load_user(user_id)
    
    register_routes(app)
    return app



if __name__ == '__main__':
    app = create_app()
    app.run()