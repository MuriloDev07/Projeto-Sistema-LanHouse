from flask import jsonify
from functools import wraps
from flask_jwt_extended import get_jwt, jwt_required, unset_access_cookies

def admin_required():
    def decorator(fn):
        """
        Decorador que garante que a rota só seja acessada por usuários com role 'admin'.
        """
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()

            if claims.get("role") != "admin":
                return jsonify({"msg": "Acesso restrito a Administradores"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def register_jwt_handlers(jwt):
    """
    Registra os callbacks de tratamento de excessões de autenticação JWT.
    """
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        response = jsonify({
            "erro": "token_expired",
            "mensagem": "Sua sessão expirou. Por favor, faça login novamente."
        })
        unset_access_cookies(response)
        return response, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "erro": "authorizathion_required",
            "mensagem": "Autenticação necessária. Faça login para acessar este recurso."
        })