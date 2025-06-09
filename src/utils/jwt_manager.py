import jwt
import datetime
from flask import current_app
import os

JWT_KEY = os.getenv('JWT_KEY')

def generar_token(usuario_id):
    payload = {
        'sub': str(usuario_id),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }
    token = jwt.encode(payload, JWT_KEY, algorithm='HS256')
    return token

def verificar_token(token):
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
        print(f"Payload decodificado: {payload}")
        return payload['sub']
    except Exception as e:
        print(f"Error decodificando token: {e}")
        return None