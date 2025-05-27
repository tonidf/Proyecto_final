from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from routes import register_routes
from config import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config["dev"])

    register_routes(app)
    return app



if __name__ == '__main__':
    app = create_app()
    app.run()