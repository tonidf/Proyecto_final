from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from extensions import mysql
from api_football import get_team_statistics, total_tarjetas # Importar la función para obtener el equipo por ID



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
    if not respuesta:
        flash("Equipo no encontrado o sin estadísticas disponibles", "error")
        return redirect(url_for('equipos.equipos'))
    cards = respuesta.get('cards', {})
    yellow_cards = cards.get('yellow', {})
    total_amarillas = total_tarjetas(yellow_cards)
    cards = respuesta.get('cards', {})
    red_cards = cards.get('yellow', {})
    total_rojas = total_tarjetas(red_cards)

    return render_template('equipo_individual.html', equipo=respuesta, equipo_cabecera=equipo_cabecera, total_amarillas=total_amarillas, total_rojas=total_rojas)