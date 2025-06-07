from flask import Blueprint, jsonify, render_template
import requests
import os

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
    return render_template('jugadores_general.html')