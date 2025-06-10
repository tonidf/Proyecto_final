import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify

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
        return payload['sub']
    except Exception as e:
        print(f"Error decodificando token: {e}")
        return None
    

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({"message": "Token faltante"}), 401

        user_id = verificar_token(token)
        if not user_id:
            return jsonify({"message": "Token inválido o expirado"}), 401

        return f(user_id=user_id, *args, **kwargs)
    return decorated