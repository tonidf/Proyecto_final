from src.app import create_app
from src.extensions import mysql
import requests
import os
import time

app = create_app()

API_FOOTBALL_URL = "https://v3.football.api-sports.io/players"
API_FOOTBALL_KEY = os.getenv("API_KEY")  # O puedes poner la clave directamente
SEASON = 2023  # Año de temporada

def obtener_api_ids_equipos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, api_id FROM equipos WHERE id IN (13, 14, 15, 20)")
    equipos = cur.fetchall()
    cur.close()
    return equipos  # Lista de tuplas (id, api_id)

def insertar_o_actualizar_jugador(jugador, equipo_id):
    player_info = jugador.get('player', {})
    nombre = player_info.get('name', '')
    nombre_lower = nombre.lower()
    posicion = player_info.get('position', '')
    foto_url = player_info.get('photo', '')

    estadisticas = jugador.get('statistics', [{}])[0]  # Primer set de estadísticas si existe
    goles = estadisticas.get('goals', {}).get('total', 0) or 0
    asistencias = estadisticas.get('goals', {}).get('assists', 0) or 0
    partidos = estadisticas.get('games', {}).get('appearences', 0) or 0

    cur = mysql.connection.cursor()
    print(f"Insertando jugador: {nombre} (equipo_id={equipo_id})")

    sql = """
        INSERT INTO jugadores (nombre, nombre_lower, posicion, foto_url, goles, asistencias, partidos, equipo_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nombre_lower=VALUES(nombre_lower),
            posicion=VALUES(posicion),
            foto_url=VALUES(foto_url),
            goles=VALUES(goles),
            asistencias=VALUES(asistencias),
            partidos=VALUES(partidos),
            equipo_id=VALUES(equipo_id)
    """
    cur.execute(sql, (nombre, nombre_lower, posicion, foto_url, goles, asistencias, partidos, equipo_id))
    mysql.connection.commit()
    cur.close()

def obtener_jugadores_desde_api(api_id_equipo):
    headers = {
        "x-apisports-key": API_FOOTBALL_KEY
    }
    jugadores = []
    page = 1
    while True:
        params = {
            "team": api_id_equipo,
            "season": SEASON,
            "page": page
        }
        response = requests.get(API_FOOTBALL_URL, headers=headers, params=params)
        print(f"    Página {page} - Código respuesta: {response.status_code}")
        if response.status_code != 200:
            print(f"    ❌ Error al obtener jugadores: {response.text}")
            break
        data = response.json()
        jugadores += data.get("response", [])
        total_pages = data.get("paging", {}).get("total", 1)
        if page >= total_pages:
            break
        page += 1
    return jugadores

def rellenar_todos_los_jugadores():
    equipos = obtener_api_ids_equipos()
    for equipo_id, api_id in equipos:
        print(f"\n Equipo {equipo_id} (API ID: {api_id})")
        jugadores = obtener_jugadores_desde_api(api_id)
        print(f"  - Jugadores recibidos: {len(jugadores)}")
        if not jugadores:
            print("  ⚠️  No se recibieron jugadores o error en la API")
        for jugador in jugadores:
            try:
                insertar_o_actualizar_jugador(jugador, equipo_id)
            except Exception as e:
                print(f"❌ Error insertando jugador: {jugador.get('player', {}).get('name')} - equipo_id={equipo_id}")
                print(f"   Detalle del error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    with app.app_context():
        rellenar_todos_los_jugadores()

