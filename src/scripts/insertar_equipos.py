import os
import requests
from src.extensions import mysql
from src.app import create_app  # Importamos create_app para inicializar la app

# Crea la app y el contexto
app = create_app()

headers = {
    'x-apisports-key': os.getenv('API_KEY')
}

params = {
    'league': 140,
    'season': 2023
}

res = requests.get("https://v3.football.api-sports.io/teams", headers=headers, params=params)
data = res.json()

equipos_sql = []
for item in data['response']:
    team = item['team']
    venue = item['venue']

    valores = (
        team['id'],
        team['name'],
        team['country'],
        team['code'] or '',
        team['logo'],
        140,
        team.get('founded') or 0,
        venue.get('name') or '',
        venue.get('capacity') or 0
    )
    equipos_sql.append(valores)

# Ejecutar dentro del contexto de la app
with app.app_context():
    cursor = mysql.connection.cursor()
    for e in equipos_sql:
        sql = f"""INSERT INTO equipos (api_id, nombre, pais, codigo, logo, league_id, founded, venue_name, venue_capacity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        cursor.execute(sql, e)  # Evita inyecciones SQL usando parámetros
        print(f"Insertado: {e[1]}")
    mysql.connection.commit()
    cursor.close()
