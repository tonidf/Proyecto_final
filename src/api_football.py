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
    'x-apisports-key': API_KEY
}



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
        return response.json()
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

def total_tarjetas(cards_data):
    return sum(v['total'] for v in cards_data.values() if v['total'] is not None)