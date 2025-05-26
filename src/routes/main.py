from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, Blueprint
from flask_mysqldb import MySQL

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def inicio():
    return render_template('inicio.html')

@main_bp.route('/general', methods=['GET', 'POST'])
def general():
    pass