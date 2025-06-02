import requests
import os

API_KEY = os.getenv('API_KEY')  # Asegúrate de que la variable de entorno
BASE_URL = 'https://v3.football.api-sports.io'

HEADERS = {
    'x-apisports-key': API_KEY
}

def get_team_statistics(team_id, league_id=140, season=2023):
    url = f"{BASE_URL}/teams/statistics"
    params = {
        "team": team_id,
        "league": league_id,
        "season": season
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None