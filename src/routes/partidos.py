from operator import ge
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
import requests
import os
from extensions import mysql
from api_football import get_rounds_from_cache, fetch_and_cache_rounds, get_fixtures_by_round, get_match_statistics

partidos_bp = Blueprint('partidos', __name__)

@partidos_bp.route('/general', methods=['GET', 'POST'])
def general():
    rounds = get_rounds_from_cache()

    if not rounds:
        rounds = fetch_and_cache_rounds()

    return render_template('general.html', rounds=rounds)

@partidos_bp.route('/partidos/<int:fixture_id>', methods=['GET'])
def obtener_partido(fixture_id):
    stats = get_match_statistics(fixture_id)  # función que llama a la API
    return render_template('partido_individual.html', stats=stats)

@partidos_bp.route('/api/partidos')
def obtener_partidos_por_jornada():
    round_name = request.args.get('round')
    league_id = 140  # Liga española
    season = 2023

    if not round_name:
        return jsonify({'error': 'No se especificó la jornada'}), 400

    partidos = get_fixtures_by_round(round_name, league_id, season)
    return jsonify(partidos)