from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from flask_mysqldb import MySQL
from api_football import get_clasificacion

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def inicio():
    return render_template('inicio.html')

@main_bp.route('/tabla')
def tabla():
    clasificacion = get_clasificacion()
    return render_template('tabla.html', clasificacion=clasificacion)