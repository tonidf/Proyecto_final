from flask import Blueprint, request, jsonify
from utils.jwt_manager import jwt_required
from extensions import mysql
from api_football import get_team_statistics, obtener_estadisticas_jugador_por_id, get_match_statistics

favoritos_bp = Blueprint('favoritos', __name__)

@favoritos_bp.route('/favoritos/equipo/<int:equipo_id>', methods=['POST'])
@jwt_required
def añadir_equipo_fav(user_id, equipo_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM equipos_fav WHERE id_usuario = %s AND id_equipo = %s", (user_id, equipo_id))
    existe = cur.fetchone()
    if existe:
        return jsonify({"message": "Ya es favorito"}), 400
    
    cur.execute("SELECT id FROM equipos WHERE api_id = %s", (equipo_id,))
    if not cur.fetchone(): 

        datos = get_team_statistics(equipo_id)
        if not datos:
            return jsonify({"message": "Equipo no encontrado"}), 404

        cur.execute("""
            INSERT INTO equipos (api_id, nombre, pais, codigo, logo, league_id, founded, venue_name, venue_capacity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            equipo_id,
            datos["team"]["name"],
            datos["team"]["country"],
            datos["team"]["code"],
            datos["team"]["logo"],
            datos["league"]["id"],
            datos["team"]["founded"],
            datos["venue"]["name"],
            datos["venue"]["capacity"]
        ))

    equipo_id = cur.fetchone()
    cur.execute("INSERT INTO equipos_fav (id_usuario, id_equipo) VALUES (%s, %s)", (user_id, equipo_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Equipo añadido a favoritos"}), 200

@favoritos_bp.route('/favoritos/equipo/<int:equipo_id>', methods=['DELETE'])
@jwt_required
def quitar_equipo_fav(user_id, equipo_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM equipos_fav WHERE usuario_id = %s AND equipo_id = %s", (user_id, equipo_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Equipo eliminado de favoritos"}), 200

@favoritos_bp.route('/favoritos/jugador/<int:jugador_id>', methods=['POST'])
@jwt_required
def añadir_jugador_fav(user_id, jugador_id):
    cur = mysql.connection.cursor()

    # Verificar si ya está en favoritos
    cur.execute("SELECT 1 FROM jugadores_fav WHERE usuario_id = %s AND jugador_id = %s", (user_id, jugador_id))
    if cur.fetchone():
        return jsonify({"message": "Ya es favorito"}), 400

    # Verificar si el jugador ya está guardado
    cur.execute("SELECT 1 FROM jugadores WHERE id = %s", (jugador_id,))
    if not cur.fetchone():
        # Aquí llamas a tu API externa
        datos = obtener_estadisticas_jugador_por_id(jugador_id)
        if not datos:
            return jsonify({"message": "Jugador no encontrado"}), 404

        cur.execute("INSERT INTO jugadores (id, nombre, equipo) VALUES (%s, %s, %s)", 
                    (jugador_id, datos['nombre'], datos['equipo']))

    # Insertar favorito
    cur.execute("INSERT INTO jugadores_fav (usuario_id, jugador_id) VALUES (%s, %s)", (user_id, jugador_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Jugador añadido a favoritos"}), 200

@favoritos_bp.route('/favoritos/jugador/<int:jugador_id>', methods=['DELETE'])
@jwt_required
def quitar_jugador_fav(user_id, jugador_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM jugadores_fav WHERE usuario_id = %s AND jugador_id = %s", (user_id, jugador_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Jugador eliminado de favoritos"}), 200

@favoritos_bp.route('/favoritos/partido/<int:partido_id>', methods=['POST'])
@jwt_required
def añadir_partido_fav(user_id, partido_id):
    cur = mysql.connection.cursor()

    # Verificar si ya es favorito
    cur.execute("SELECT 1 FROM partidos_fav WHERE usuario_id = %s AND partido_id = %s", (user_id, partido_id))
    if cur.fetchone():
        return jsonify({"message": "Ya está en favoritos"}), 400

    # Verificar si el partido ya está en la base de datos
    cur.execute("SELECT 1 FROM partidos WHERE id = %s", (partido_id,))
    if not cur.fetchone():
        # Si no está, llamamos a tu función ya existente
        datos = get_match_statistics(partido_id)
        if not datos:
            return jsonify({"message": "Partido no encontrado"}), 404

        # Inserta el partido (ajusta los campos a tu modelo)
        cur.execute("""
            INSERT INTO partidos (id, fecha, equipo_local, equipo_visitante, goles_local, goles_visitante)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            partido_id,
            datos['fecha'],
            datos['equipo_local'],
            datos['equipo_visitante'],
            datos['goles_local'],
            datos['goles_visitante']
        ))

    # Insertar en favoritos
    cur.execute("INSERT INTO partidos_fav (usuario_id, partido_id) VALUES (%s, %s)", (user_id, partido_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Partido añadido a favoritos"}), 200

@favoritos_bp.route('/favoritos/partido/<int:partido_id>', methods=['DELETE'])
@jwt_required
def quitar_partido_fav(user_id, partido_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM partidos_fav WHERE usuario_id = %s AND partido_id = %s", (user_id, partido_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Partido eliminado de favoritos"}), 200