from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from extensions import mysql



equipos_bp = Blueprint('equipos', __name__)

@equipos_bp.route('/equipos', methods=['GET', 'POST'])
def equipos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, logo FROM equipos")
    equipos = cursor.fetchall()

    return render_template('equipos.html', equipos=equipos)