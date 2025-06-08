from flask import Blueprint, jsonify, render_template, request, redirect, url_for
import requests
import os
from api_football import obtener_jugadores_por_equipo, buscar_jugadores_por_nombre, obtener_estadisticas_jugador, obtener_todos_los_equipos, test_api_key

API_KEY = os.getenv('API_KEY')

players_bp = Blueprint('players', __name__)



@players_bp.route('/buscar/<nombre>')
def buscar_jugador(nombre):
    url = "https://v3.football.api-sports.io/players?search={}&season=2023".format(nombre)
    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

@players_bp.route('/jugadores/general')
def jugadores_general():
    test_api_key()  # Verifica si la clave API es válida
    equipos = obtener_todos_los_equipos()  # Implementa esta función para obtener todos los equipos
    return render_template('jugadores_general.html', equipos=equipos)


@players_bp.route('/api/jugadores_top5')
def jugadores_top5():
    equipo_id = request.args.get('equipo_id')
    print("Equipo ID recibido:", equipo_id)
    if not equipo_id:
        return jsonify([])

    jugadores = obtener_jugadores_por_equipo(equipo_id)  # Devuelve lista de dicts con 'goles' y 'asistencias'
    print("Jugadores crudos:", jugadores)
    # Filtrar jugadores que tengan al menos un gol o asistencia
    jugadores_con_contribuciones = [j for j in jugadores if (j['goles'] + j['asistencias']) > 0]

    # Si quieres mostrar solo jugadores con contribuciones, usar la lista filtrada; si quieres incluir todos, usa 'jugadores'
    lista_a_ordenar = jugadores_con_contribuciones if jugadores_con_contribuciones else jugadores

    # Ordenar por suma goles + asistencias descendente
    top5 = sorted(
    jugadores,
    key=lambda x: (x['goles'] + x['asistencias']),
    reverse=True
    )[:5]

    return jsonify(top5)

@players_bp.route('/buscar_jugadores')
def buscar_jugadores():
    nombre = request.args.get('nombre', '').strip().lower()
    if not nombre or len(nombre) < 2:
        return jsonify([])

    # Aquí deberías consultar tu base de datos o API externa
    jugadores = buscar_jugadores_por_nombre(nombre)  # Implementa esta función

    resultados = [{'nombre': jugador['nombre']} for jugador in jugadores]
    return jsonify(resultados)

@players_bp.route('/comparar-jugadores')
def comparar_jugadores():
    nombre1 = request.args.get('jugador1')
    nombre2 = request.args.get('jugador2')

    if not nombre1 or not nombre2:
        return redirect(url_for('player.jugadores_general'))  # o muestra un error

    jugador1 = obtener_estadisticas_jugador(nombre1)  # Implementa esta función
    jugador2 = obtener_estadisticas_jugador(nombre2)

    return render_template('comparar_jugadores.html', jugador1=jugador1, jugador2=jugador2)