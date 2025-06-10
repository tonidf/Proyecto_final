from flask import Blueprint, jsonify, render_template, request, redirect, url_for
import requests
import os
from extensions import mysql
from api_football import obtener_jugadores_por_equipo, buscar_jugadores_por_nombre, obtener_estadisticas_jugador, obtener_todos_los_equipos, obtener_foto_jugador

API_KEY = os.getenv('API_KEY')

players_bp = Blueprint('players', __name__)

API_ID_A_INTERNO = {
    529: 1, 530: 2, 531: 3, 532: 4, 533: 5, 534: 6, 536: 7, 538: 8, 541: 9, 542: 10,
    543: 11, 546: 12, 547: 13, 548: 14, 715: 15, 723: 16, 724: 17, 727: 18, 728: 19,
    798: 20
}

@players_bp.route('/jugador/<int:jugador_id>')
def jugador_por_id(jugador_id):
    url = f"https://v3.football.api-sports.io/players?id={jugador_id}&season=2023&league=140"
    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if not data["response"]:
        return render_template("jugador_no_encontrado.html")

    jugador = data["response"][0]
    print(f"Datos del jugador: {jugador}")
    return render_template("jugador_unico.html", jugador=jugador)

@players_bp.route('/jugadores/general')
def jugadores_general(): 
    equipos = obtener_todos_los_equipos()  # Implementa esta función para obtener todos los equipos
    return render_template('jugadores_general.html', equipos=equipos)


@players_bp.route('/api/jugadores_top5')
def jugadores_top5():
    equipo_api_id = request.args.get('equipo_id')
    if not equipo_api_id:
        return jsonify([])

    try:
        equipo_api_id_int = int(equipo_api_id)
    except ValueError:
        return jsonify([])

    equipo_interno_id = API_ID_A_INTERNO.get(equipo_api_id_int)
    if not equipo_interno_id:
        return jsonify([])  # No encontrado

    # Aquí usas equipo_api_id_int para llamar a la API externa
    jugadores = obtener_jugadores_por_equipo(equipo_api_id_int)

    # Luego si quieres filtrar en base a equipo interno, o usar equipo_interno_id en la DB para otros fines

    # Resto del código igual...
    jugadores_con_contribuciones = [j for j in jugadores if (j['goles'] + j['asistencias']) > 0]
    lista_a_ordenar = jugadores_con_contribuciones if jugadores_con_contribuciones else jugadores

    top5 = sorted(
    lista_a_ordenar,
    key=lambda x: (x['goles'] + x['asistencias']),
    reverse=True
    )[:5]

    for jugador in top5:
        foto = obtener_foto_jugador(jugador['nombre'])
        if not foto:
            jugador['foto'] = url_for('static', filename='img/profile_default.webp')
        else:
            jugador['foto'] = foto
        # Asegúrate que jugador tiene 'id' ya en la data; si no, obténlo aquí.

    return jsonify(top5)




@players_bp.route('/buscar_jugadores')
def buscar_jugador():
    nombre = request.args.get('nombre', '').strip()
    if len(nombre) < 4:
        return jsonify([])

    url = f"https://v3.football.api-sports.io/players?search={nombre}&season=2023&league=140"
    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify([])

    data = response.json()
    print(f"Datos de la búsqueda: {data}")
    jugadores = data.get("response", [])

    resultados = []
    ya_vistos = set()
    for j in jugadores:
        jugador_data = j.get("player", {})
        nombre_jugador = jugador_data.get("name")
        id_jugador = jugador_data.get("id")

        if nombre_jugador and id_jugador and nombre_jugador not in ya_vistos:
            resultados.append({
                "id": id_jugador,
                "nombre": nombre_jugador
            })
            ya_vistos.add(nombre_jugador)

    return jsonify(resultados[:10])


@players_bp.route('/comparar-jugadores')
def comparar_jugadores():
    nombre1 = request.args.get('jugador1')
    nombre2 = request.args.get('jugador2')

    if not nombre1 or not nombre2:
        return redirect(url_for('player.jugadores_general'))  # o muestra un error

    jugador1 = obtener_estadisticas_jugador(nombre1)  # Implementa esta función
    jugador2 = obtener_estadisticas_jugador(nombre2)
    print(f"Jugador 1: {jugador1}")
    print(f"Jugador 2: {jugador2}")
    return render_template('comparar_jugadores.html', jugador1=jugador1, jugador2=jugador2)
