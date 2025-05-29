import requests
import os
from src.extensions import mysql
from flask import current_app

headers = {
    'x-apisports-key': os.getenv('API_KEY')   # Reemplaza con tu key real
}

params = {
    'league': 140,     # La Liga
    'season': 2023
}

res = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params=params)
data = res.json()

# Prepara lista de equipos para SQL
equipos_sql = []
for item in data['response']:
    team = item['team']
    venue = item['venue']

    valores = (
        team['id'],                      # api_id
        team['name'],                   # nombre
        team['country'],                # pais
        team['code'] or '',             # codigo
        team['logo'],                   # logo
        140,                            # league_id (La Liga)
        team.get('founded') or 0,       # founded
        venue.get('name') or '',        # estadio
        venue.get('capacity') or 0      # capacidad
    )
    equipos_sql.append(valores)
with current_app.app_context():
    cursor = mysql.connection.cursor()
    for e in equipos_sql:
        sql = f"""INSERT INTO equipos (api_id, nombre, pais, codigo, logo, league_id, founded, venue_name, venue_capacity)
                VALUES ({e[0]}, '{e[1]}', '{e[2]}', '{e[3]}', '{e[4]}', {e[5]}, {e[6]}, '{e[7]}', {e[8]});"""
        cursor.execute(sql)
        print(sql)
    mysql.connection.commit()
    cursor.close()
