from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    register_blueprints(app)
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)