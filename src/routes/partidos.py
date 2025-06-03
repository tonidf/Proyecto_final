from operator import ge
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
import requests
import os
from extensions import mysql
from api_football import get_rounds_from_cache, fetch_and_cache_rounds

partidos_bp = Blueprint('partidos', __name__)

@partidos_bp.route('/general', methods=['GET', 'POST'])
def general():
    rounds = get_rounds_from_cache()

    if not rounds:
        rounds = fetch_and_cache_rounds()

    return render_template('general.html', rounds=rounds)