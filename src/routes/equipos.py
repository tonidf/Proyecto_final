from sqlite3 import Cursor
from tkinter import N
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from extensions import mysql
from api_football import get_team_statistics # Importar la función para obtener el equipo por ID



equipos_bp = Blueprint('equipos', __name__)

@equipos_bp.route('/equipos', methods=['GET', 'POST'])
def equipos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT api_id, logo FROM equipos")
    equipos = cursor.fetchall()

    return render_template('equipos.html', equipos=equipos)

@equipos_bp.route('/equipos/<int:equipo_id>', methods=['GET'])
def get_equipo(equipo_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre, logo, founded FROM equipos WHERE api_id = %s", (equipo_id,))
    equipo_cabecera = cursor.fetchone()
    
    respuesta = get_team_statistics(equipo_id)
    if not respuesta or 'response' not in respuesta:
        flash("Equipo no encontrado o sin estadísticas disponibles", "error")
        return redirect(url_for('equipos.equipos'))
    equipo = respuesta['response']
    

    return render_template('equipo.html', equipo=equipo, equipo_cabecera=equipo_cabecera)