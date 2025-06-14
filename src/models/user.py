from flask_login import UserMixin
from extensions import mysql
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def set_password(self, password):
        return generate_password_hash(password)
    
    def check_password(self, password, hashed_password):
        return check_password_hash(hashed_password, password)
    


