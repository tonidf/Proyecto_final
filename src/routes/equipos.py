from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from extensions import mysql
from api_football import get_team_statistics, total_tarjetas, get_clasificacion # Importar la función para obtener el equipo por ID
import jwt
import os

SECRET_KEY = os.getenv('JWT_KEY')

equipos_bp = Blueprint('equipos', __name__)

@equipos_bp.route('/equipos', methods=['GET'])
def equipos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT api_id, logo FROM equipos")
    equipos = cursor.fetchall()

    favoritos = []

    # Intentar obtener el token desde las cookies
    token = request.cookies.get('access_token')
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data.get("sub")
            cursor.execute("SELECT id_equipo FROM equipos_fav WHERE id_usuario = %s", (user_id,))
            favoritos = [row[0] for row in cursor.fetchall()]
        except jwt.ExpiredSignatureError:
            print("Token expirado")
        except jwt.InvalidTokenError:
            print("Token inválido")

    cursor.close()
    return render_template('equipos.html', equipos=equipos, favoritos=favoritos)

@equipos_bp.route('/equipos/<int:equipo_id>', methods=['GET'])
def get_equipo(equipo_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre, logo, founded FROM equipos WHERE api_id = %s", (equipo_id,))
    equipo_cabecera = cursor.fetchone()
    clasificacion = get_clasificacion()
    
    respuesta = get_team_statistics(equipo_id)
    if not respuesta:
        flash("Equipo no encontrado o sin estadísticas disponibles", "error")
        return redirect(url_for('equipos.equipos'))
    cards = respuesta.get('cards', {})
    yellow_cards = cards.get('yellow', {})
    total_amarillas = total_tarjetas(yellow_cards)
    cards = respuesta.get('cards', {})
    red_cards = cards.get('red', {})
    total_rojas = total_tarjetas(red_cards)

    return render_template('equipo_individual.html', equipo=respuesta, equipo_cabecera=equipo_cabecera, total_amarillas=total_amarillas, total_rojas=total_rojas, clasificacion=clasificacion)

@equipos_bp.route('/buscar_equipos')
def buscar_equipos():
    nombre = request.args.get('nombre', '').lower()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre, logo FROM equipos WHERE LOWER(nombre) LIKE %s LIMIT 10", ('%' + nombre + '%',))
    resultados = cursor.fetchall()

    equipos = [{"nombre": row[0], "logo": row[1]} for row in resultados]

    return jsonify(equipos)