from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from flask_mysqldb import MySQL

equipos_bp = Blueprint('equipos', __name__)

@equipos_bp.route('/equipos', methods=['GET', 'POST'])
def equipos():
    return render_template('equipos.html')