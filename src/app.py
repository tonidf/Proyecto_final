from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)


# Conexión a la base de datos
db = MySQL(app)

@app.route('/')
def index():
    return render_template('inicio.html')