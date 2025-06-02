from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from extensions import mysql
from api_football import get_team_statistics # Importar la función para obtener el equipo por ID



equipos_bp = Blueprint('equipos', __name__)

@equipos_bp.route('/equipos', methods=['GET', 'POST'])
def equipos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, logo FROM equipos")
    equipos = cursor.fetchall()

    return render_template('equipos.html', equipos=equipos)

@equipos_bp.route('/equipos/<int:equipo_id>', methods=['GET'])
def get_equipo(equipo_id):
    equipo = get_team_statistics(equipo_id)
    if not equipo:
        flash("Equipo no encontrado", "error")
        return redirect(url_for('equipos.equipos'))
    

    return render_template('equipo.html', equipo=equipo)