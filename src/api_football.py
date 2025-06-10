from flask import url_for
import requests
import os
import json
from datetime import datetime, timedelta
from extensions import mysql
import MySQLdb.cursors
import re

CACHE_DURATION_HOURS = 24

API_KEY = os.getenv('API_KEY')  
BASE_URL = 'https://v3.football.api-sports.io'
HEADERS = {
    'x-apisports-key': API_KEY,
    'User-Agent': 'FutStats-TFG/1.0'
}

def test_api_key():
    url = "https://v3.football.api-sports.io/status"
    response = requests.get(url, headers=HEADERS)
    print("Código:", response.status_code)
    print("Respuesta:", response.json())

# Esta función intenta recuperar estadísticas cacheadas de la base de datos
def get_cached_statistics(team_id, league_id, season):
    # Crear un cursor que devuelva los resultados como diccionarios
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Ejecutar una consulta para buscar estadísticas existentes para el equipo, liga y temporada
    cursor.execute("SELECT data, updated_at FROM estadisticas_cache WHERE team_id = %s AND league_id = %s AND season = %s", (team_id, league_id, season))
    
    # Obtener la primera fila de resultados
    row = cursor.fetchone()
    
    if row:
        # Extraer la fecha de actualización
        updated_at = row['updated_at']
        
        # Comprobar si la caché todavía es válida (menos de X horas desde que se guardó)
        if updated_at > datetime.now() - timedelta(hours=CACHE_DURATION_HOURS):
            # Devolver los datos en formato JSON (ya que se almacenaron como string)
            return json.loads(row['data'])
    
    # Si no hay datos o están caducados, devolver None
    return None

# Esta función guarda (o actualiza) las estadísticas en la tabla de caché
def save_statistics_to_cache(team_id, league_id, season, data):
    # Crear un cursor para ejecutar la consulta
    cursor = mysql.connection.cursor()
    
    # Insertar los datos o actualizarlos si ya existen para ese equipo, liga y temporada
    cursor.execute("""
        INSERT INTO estadisticas_cache (team_id, league_id, season, data, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE data = VALUES(data), updated_at = VALUES(updated_at)
    """, (
        team_id,                   # ID del equipo
        league_id,                # ID de la liga
        season,                   # Temporada
        json.dumps(data),         # Convertimos el JSON a string para guardar
        datetime.now()            # Timestamp actual para saber cuándo se actualizó la caché
    ))
    
    # Confirmar los cambios en la base de datos
    mysql.connection.commit()



def get_team_statistics(team_id, league_id=140, season=2023):

    cached = get_cached_statistics(team_id, league_id, season)
    if cached:
        return cached

    url = f"{BASE_URL}/teams/statistics"
    params = {
        "team": team_id,
        "league": league_id,
        "season": season
    }

    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json().get("response")

    if response.status_code == 200:
        save_statistics_to_cache(team_id, league_id, season, data)
        return data
    else:
        print(f"Error: {response.status_code}")
        return None
    
def save_rounds_to_cache(rounds, league_id, season):
    cursor = mysql.connection.cursor()
    for round_name in rounds:
        cursor.execute("INSERT IGNORE INTO rounds_cache (league_id, season, round_name)VALUES (%s, %s, %s)", (league_id, season, round_name))
    mysql.connection.commit()

def fetch_and_cache_rounds(league_id=140, season=2023):
    url = f"{BASE_URL}/fixtures/rounds"
    params = {
        "league": league_id,
        "season": season
    }
    

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        rounds = data.get("response", [])
        save_rounds_to_cache(rounds, league_id, season)
        return rounds
    else:
        return []
    

def get_rounds_from_cache(league_id=140, season=2023):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT round_name FROM rounds_cache WHERE league_id = %s AND season = %s ORDER BY round_name", (league_id, season))
    rounds = [row[0] for row in cursor.fetchall()]

    def extract_number(round_name):
        match = re.search(r'(\d+)', round_name)
        return int(match.group(1)) if match else 0

    rounds.sort(key=extract_number)

    return rounds

def get_cached_fixtures(round_name, league_id, season):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT data, updated_at FROM fixtures_cache WHERE round_name = %s AND league_id = %s AND season = %s", (round_name, league_id, season))
    row = cursor.fetchone()
    if row:
        updated_at = row[1]
        if updated_at > datetime.now() - timedelta(hours=CACHE_DURATION_HOURS):
            return json.loads(row[0])  # devuelve los datos desde la caché
    return None

def save_fixtures_to_cache(round_name, league_id, season, data):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO fixtures_cache (round_name, league_id, season, data, updated_at) VALUES (%s, %s,%s,%s, %s) ON DUPLICATE KEY UPDATE data = VALUES(data), updated_at = VALUES(updated_at)", (round_name, league_id, season, json.dumps(data), datetime.now()))
    mysql.connection.commit()

def get_fixtures_by_round(round_name, league_id, season):
    # 1. Intenta recuperar de la caché
    cached = get_cached_fixtures(round_name, league_id, season)
    if cached:
        print("Usando datos de caché para:", round_name)
        return cached

    # 2. Si no hay caché válida, llama a la API
    url = "https://v3.football.api-sports.io/fixtures"

    params = {
        "league": league_id,
        "season": season,
        "round": round_name
    }
    print("Llamando a la API con:", params)

    
    response = requests.get(url, headers=HEADERS, params=params)
    print("Código de respuesta:", response.status_code)
    if response.status_code == 200:
        data = response.json().get("response", [])
        print("Partidos recibidos:", data)
        save_fixtures_to_cache(round_name, league_id, season, data)
        return data
    else:
        return []
    
def get_match_statistics(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # La API devuelve una lista con estadísticas por equipo
        return data['response']  # Lista con dos objetos: [home_team_stats, away_team_stats]

    except requests.RequestException as e:
        print(f"Error al obtener estadísticas del partido {fixture_id}: {e}")
        return []

def get_match_lineups(fixture_id):
    url = "https://v3.football.api-sports.io/fixtures/lineups"
    params = {
        "fixture": fixture_id
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("response", [])
    else:
        print(f"Error al obtener alineaciones: {response.status_code}")
        return []
    
def get_match_result(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures?id={fixture_id}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    fixture_data = data['response'][0]
    goals_home = fixture_data['goals']['home']
    goals_away = fixture_data['goals']['away']

    return goals_home, goals_away

def obtener_partido_destacado(partidos):
    partido_destacado = None
    max_goles = -1

    for partido in partidos:
        goles_local = partido['goals']['home'] or 0
        goles_visitante = partido['goals']['away'] or 0
        total_goles = goles_local + goles_visitante

        if total_goles > max_goles:
            max_goles = total_goles
            partido_destacado = partido

    return partido_destacado


def get_clasificacion(league_id=140, season=2023):
    url = f"{BASE_URL}/standings?league={league_id}&season={season}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    clasificacion = []
    if data['response']:
        equipos = data['response'][0]['league']['standings'][0]

        for idx, equipo in enumerate(equipos, start=1):
            ultimos_resultados = []
            form = equipo.get('form', '')
            for resultado in form[-5:]:
                if resultado == 'W':
                    ultimos_resultados.append('V')
                elif resultado == 'D':
                    ultimos_resultados.append('E')
                elif resultado == 'L':
                    ultimos_resultados.append('D')

            stats = equipo['all']
            goles_favor = stats['goals']['for']
            goles_contra = stats['goals']['against']
            diferencia = goles_favor - goles_contra

            # Determinar zona según posición
            if idx <= 4:
                zona = 'champions'
            elif idx <= 6:
                zona = 'europa'
            elif idx <= 7:
                zona = 'conference'
            elif idx >= 18:
                zona = 'descenso'
            else:
                zona = None

            clasificacion.append({
                'api_id': equipo['team']['id'],
                'nombre': equipo['team']['name'],
                'logo': equipo['team']['logo'],
                'ultimos5': ultimos_resultados,
                'puntos': equipo['points'],
                'jugados': stats['played'],
                'ganados': stats['win'],
                'empatados': stats['draw'],
                'perdidos': stats['lose'],
                'goles_a_favor': goles_favor,
                'goles_en_contra': goles_contra,
                'diferencia_goles': diferencia,
                'zona': zona,
            })

    return clasificacion

def obtener_team_id_por_nombre(nombre):
    cur = mysql.connection.cursor()
    cur.execute("SELECT api_id FROM equipos WHERE nombre = %s", (nombre,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

def total_tarjetas(cards_data):
    return sum(v['total'] for v in cards_data.values() if v['total'] is not None)


def obtener_jugadores_por_equipo(equipo_id, season=2023):
    jugadores = []
    page = 1
    url = f"{BASE_URL}/players"
    print("API_KEY:", API_KEY)  # Para depuración, asegúrate de que la clave se carga correctamente

    while True:
        params = {
            'team': equipo_id,
            'season': season,
            'page': page
        }
        print("HEADERS que se envían:", HEADERS)
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Error en la API: {response.status_code}")
            print(response.text)
            break
        
        data = response.json()
        print("Datos recibidos de la API:", data)  # Para depuración
        jugadores_pagina = data.get('response', [])
        print(json.dumps(data, indent=2))

        if not jugadores_pagina:
            break
        
        for jugador in jugadores_pagina:
            stats = jugador.get('statistics', [{}])[0]
            goles = stats.get('goals', {}).get('total')
            asistencias = stats.get('goals', {}).get('assists')
            partidos = stats.get('games', {}).get('appearences')

            jugador_info = {
                'nombre': jugador.get('player', {}).get('name', 'Desconocido'),
                'goles': goles if goles is not None else 0,
                'asistencias': asistencias if asistencias is not None else 0,
                'partidos': partidos if partidos is not None else 0
            }
            jugadores.append(jugador_info)
        
        total_pages = data.get('paging', {}).get('total', 1)
        if page >= total_pages:
            break
        
        page += 1

    print("ESTOS SON LOS JUGADORES:", jugadores)
    return jugadores

def buscar_jugadores_por_nombre(nombre):
    url = 'https://v3.football.api-sports.io/players'
    params = {
        'search': nombre,
        'season': 2023
    }

    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    jugadores = []
    for item in data['response']:
        jugadores.append({
            'nombre': item['player']['name']
        })

    return jugadores

def obtener_estadisticas_jugador(nombre):
    url = 'https://v3.football.api-sports.io/players'
    params = {
        'search': nombre,
        'season': 2023
    }

    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if not data['response']:
        return None

    jugador = data['response'][0]
    stats = jugador['statistics'][0]

    return {
        'nombre': jugador['player']['name'],
        'edad': jugador['player']['age'],
        'posicion': stats['games']['position'],
        'equipo': stats['team']['name'],
        'goles': stats['goals']['total'] or 0,
        'asistencias': stats['goals']['assists'] or 0,
        'partidos': stats['games']['appearences'] or 0,
        'imagen': jugador['player']['photo']
    }

def obtener_todos_los_equipos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT api_id, nombre, logo FROM equipos ORDER BY nombre")
    equipos = cursor.fetchall()
    cursor.close()
    return equipos

def obtener_foto_jugador(nombre_jugador):
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={nombre_jugador}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return url_for('static', filename='img/profile_default.webp')
        
        data = response.json()
        jugadores = data.get('player', [])
        for jugador in jugadores:
            # Comparación estricta por nombre (puedes usar .lower() si quieres que sea case-insensitive)
            if jugador.get('strPlayer') == nombre_jugador and jugador.get('strCutout'):
                return jugador['strCutout']
    except Exception:
        pass
    return url_for('static', filename='img/profile_default.webp')