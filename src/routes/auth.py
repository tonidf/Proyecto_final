from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from models.user import User 
from models.entities.modelUser import ModelUser
from werkzeug.security import check_password_hash
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from utils.jwt_manager import generar_token, verificar_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        user = ModelUser.Login_user(email, password)
        print(f"Email recibido: {email}")
        print(f"Usuario encontrado: {user}")
        if user and check_password_hash(user.password, password):
            token = generar_token(user.id)
            flash("Inicio de sesión exitoso")

            response = make_response(redirect(url_for('main.inicio')))
            response.set_cookie('access_token', token, httponly=True, max_age=86400)
            return response
        else:
            flash("Credenciales incorrectas")
    # Si GET o validación falla
    return render_template('login.html', form=login_form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():  # Esto valida y comprueba POST
        nombre = form.nombre.data
        email = form.email.data
        password = form.password.data

        user = ModelUser.register_user(nombre, email, password)

        if user:
            token = generar_token(user.id)
            flash("Registrado correctamente")

            response = make_response(redirect(url_for('main.inicio')))
            response.set_cookie('access_token', token, httponly=True, max_age=86400)
            return response
        else:
            flash("Error al registrar usuario.")
    return render_template('register.html', form=form)

@auth_bp.route('/profile')
def profile():
    token = request.cookies.get('access_token')
    if not token:
        flash("No estás autenticado")
        return redirect(url_for('auth.login'))
    
    user_id = verificar_token(token)
    if not user_id:
        flash("Token inválido o expirado")
        return redirect(url_for('auth.login'))

    user = ModelUser.load_user(user_id)
    if not user:
        flash("Usuario no encontrado")
        return redirect(url_for('auth.login'))

    return render_template('profile.html', user=user)

@auth_bp.route('/logout')
def logout():
    response = make_response(redirect(url_for('auth.login')))
    response.delete_cookie('access_token')
    flash("Sesión cerrada correctamente")
    return response

