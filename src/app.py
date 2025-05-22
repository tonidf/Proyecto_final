from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from src.routes.players import players_bp

app = Flask(__name__)

# Agrupacion de blueprints
app.register_blueprint(players_bp, url_prefix='/players')


# Conexión a la base de datos
db = MySQL(app)

@app.route('/')
def index():
    return render_template('inicio.html')



if __name__ == '__main__':
    app.run(debug=True)