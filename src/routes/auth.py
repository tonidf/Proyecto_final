from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user import User  # Clase que hereda de UserMixin
from models.entities.modelUser import ModelUser  # Acceso a la lógica DB
from werkzeug.security import check_password_hash


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = ModelUser.login(email, password)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))  # Cambia a tu página principal
        else:
            flash("Credenciales incorrectas")

    return render_template('auth/login.html')