from flask_login import UserMixin
from extensions import mysql, login_manager
from werkzeug.security import generate_password_hash

class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.username = name
        self.email = email
        self.password = password

    def set_password(self, password):
        return generate_password_hash(password)
    


