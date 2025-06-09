from flask import flash
from models.user import User
from extensions import mysql


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
                
                user = User(id, nombre, email, None)
                return user
            return None
        except Exception as e:
            print(e)
            flash("Error al cargar el usuario", "error")
            return None
    
    @classmethod
    def Login_user(cls, email, password):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
            data = cur.fetchone()

            if data:
                id = data[0]
                nombre = data[1]
                email = data[3]
                hashed_pass = data[2]
                user = User(id, nombre, email, hashed_pass)

                if user.check_password(password, hashed_pass):
                    return user
                else:
                    flash("Contraseña incorrecta", "error")
                    print("Contraseña incorrecta")
                    return None
                    
            else:
                flash("Usuario no encontrado", "error")
                print("Usuario no encontrado")
                return None
        except Exception as e:
            print(e)
            flash("Error al iniciar sesión", "error")
            return None
    
    @classmethod
    def register_user(cls, nombre, email, password):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE correo = %s", (email,))
            existing_user = cur.fetchone()
            
            if existing_user:
                flash("El email ya está registrado", "error")
                print("El email ya está registrado")
                return None

            hashed_pass = User.set_password(User, password)
            cur.execute(
                "INSERT INTO usuarios (nombre_completo, correo, contrasena) VALUES (%s, %s, %s)",
                (nombre, email, hashed_pass)
            )
            mysql.connection.commit()

            user_id = cur.lastrowid
            cur.close()

            return User(id=user_id, name=nombre, email=email, password=hashed_pass)

        except Exception as e:
            print(e)
            flash("Error al registrar el usuario", "error")
            return None
