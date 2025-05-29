from flask_login import UserMixin
from extensions import mysql, login_manager

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username FROM usuarios WHERE id = %s", (user_id,))
    data = cursor.fetchone()
    if data:
        return User(id=data[0], username=data[1])
    return None