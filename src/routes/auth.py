from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user import User 
from models.entities.modelUser import ModelUser  # Acceso a la lógica DB
from werkzeug.security import check_password_hash
from forms.login_form import LoginForm # Formularios para login y registro


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = ModelUser.login(email, password)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.inicio'))  
        else:
            flash("Credenciales incorrectas")

    return render_template('login.html', form=login_form)

@auth_bp.route('/register', methods=['GET', 'POST'])
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
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))