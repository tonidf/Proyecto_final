from flask import request, jsonify, render_template, redirect, url_for, flash, Blueprint
from api_football import get_rounds_from_cache, fetch_and_cache_rounds, get_fixtures_by_round, get_match_statistics, get_match_lineups, get_match_result, get_clasificacion

partidos_bp = Blueprint('partidos', __name__)

@partidos_bp.route('/general', methods=['GET', 'POST'])
def general():
    rounds = get_rounds_from_cache()

    clasificacion = get_clasificacion()
    if not rounds:
        rounds = fetch_and_cache_rounds()

    return render_template('general.html', rounds=rounds, clasificacion=clasificacion)

@partidos_bp.route('/partidos/<int:fixture_id>', methods=['GET'])
def obtener_partido(fixture_id):
    stats = get_match_statistics(fixture_id)  # función que llama a la API
    lineups = get_match_lineups(fixture_id)
    team1 = stats[0]['team']
    team2 = stats[1]['team']
    goals_home, goals_away = get_match_result(fixture_id)
    print(lineups)
    return render_template('partido_individual.html', stats=stats, team1=team1, team2=team2, lineups=lineups, score1=goals_home, score2=goals_away)

@partidos_bp.route('/api/partidos')
def obtener_partidos_por_jornada():
    round_name = request.args.get('round')
    league_id = 140  # Liga española
    season = 2023

    if not round_name:
        return jsonify({'error': 'No se especificó la jornada'}), 400

    partidos = get_fixtures_by_round(round_name, league_id, season)
    return jsonify(partidos)