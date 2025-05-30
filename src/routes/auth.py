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
            return redirect(url_for('main.inicio'))  
        else:
            flash("Credenciales incorrectas")

    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        
        user = ModelUser.register(nombre, email, password)

        if user:
            login_user(user)  
            flash("Registrado correctamente")
            return redirect(url_for('main.inicio'))  
        else:
            flash("Error al registrar usuario.")
    
    return render_template('auth/register.html')

# 🚪 LOGOUT
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))