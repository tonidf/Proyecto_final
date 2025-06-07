from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from flask_mysqldb import MySQL
from api_football import get_clasificacion, get_team_statistics, obtener_team_id_por_nombre

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def inicio():
    return render_template('inicio.html')

@main_bp.route('/tabla')
def tabla():
    clasificacion = get_clasificacion()
    return render_template('tabla.html', clasificacion=clasificacion)

@main_bp.route('/comparar')
def comparar():
    equipo1 = request.args.get('equipo1')
    equipo2 = request.args.get('equipo2')

    estadisticas1 = estadisticas2 = None

    if equipo1 and equipo2:
        id1 = obtener_team_id_por_nombre(equipo1)
        id2 = obtener_team_id_por_nombre(equipo2)

        if id1 and id2:
            estadisticas1 = get_team_statistics(id1)
            estadisticas2 = get_team_statistics(id2)
        else:
            error = "Uno o ambos equipos no están en la base de datos."
            return render_template('comparar.html', error=error)
    print(estadisticas1, estadisticas2)

    return render_template('comparar.html', equipo1=estadisticas1, equipo2=estadisticas2)