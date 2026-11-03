from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required

def admin_required():
    def decorator(fn):
        """
        Decorador que garante que a rota só seja acessada por usuários com role 'admin'.
        """
        @wraps(fn)
        @jwt_required()
        def wraper(*args, **kwargs):
            claims = get_jwt()

            if claims.get("role") != "admin":
                return jsonify({"msg": "Acesso restrito a Administradores"}), 403

            return fn(*args, **kwargs)
        return wraper
    return decorator