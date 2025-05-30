from flask import flash, request
from user import User
from extensions import mysql, login_manager


class ModelUser:

    @classmethod
    def load_user(cls,id):
        try: 
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
            data = cur.fetchone()

            if data:
                id = data[0]
                nombre = data[1]
                email = data[2]
                
                user = User(id, nombre, None, email)
                return user
            return None
        except Exception as e:
            print(e)
            flash("Error al cargar el usuario", "error")
            return None
    
    @classmethod
    def login_user(cls, email, password):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            data = cur.fetchone()

            if data:
                id = data[0]
                nombre = data[1]
                email = data[2]
                hashed_pass = data[3]

                user = User(id, nombre, email, hashed_pass)

                if user.check_password(password, hashed_pass):
                    return user
                else:
                    flash("Contraseña incorrecta", "error")
                    return None
            else:
                flash("Usuario no encontrado", "error")
                return None
        except Exception as e:
            print(e)
            flash("Error al iniciar sesión", "error")
            return None
    
    @classmethod
    def register_user(cls, nombre, email, password):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                flash("El email ya está registrado", "error")
                return False
            hashed_pass = User.set_password(User, password)
            cur.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", (nombre, email, hashed_pass))
            mysql.connection.commit()
            flash("Usuario registrado correctamente", "success")
            return True
        except Exception as e:
            print(e)
            flash("Error al registrar el usuario", "error")
            return False
