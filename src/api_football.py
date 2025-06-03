import requests
import os
import json
from datetime import datetime, timedelta
from extensions import mysql
import MySQLdb.cursors

CACHE_DURATION_HOURS = 12

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

def total_tarjetas(cards_data):
    return sum(v['total'] for v in cards_data.values() if v['total'] is not None)