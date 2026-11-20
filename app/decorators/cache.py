import json
from functools import wraps
from flask import current_app, jsonify
from app.core.cache import redis_client

def invalidate_cache(chave: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs): 
            response = func(*args, **kwargs)
            status = response[1] if isinstance(response, tuple) else response.status_code
            if status in (200, 201):
                try:
                    redis_client.delete(chave)
                    current_app.logger.info(f"Cache invalidado com sucesso: '{chave}'")
                except Exception as err:
                    current_app.logger.error(f"Falha ao invalidar cache '{chave}' no Redis: {err}")
            return response
        return wrapper
    return decorator

def cache_aside(chave: str, ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                cached_data = redis_client.get(chave)
                if cached_data:
                    current_app.logger.info(f"Cache HIT: Dados recuperados no Redis para '{chave}'")
                    payload = json.loads(cached_data)
                    if isinstance(payload, dict) and "mensagem" in payload:
                        payload['mensagem'] = payload['mensagem'].replace("(Banco)", "(Cache)")
                    return jsonify(payload), 200
            except Exception as err:
                current_app.logger.error(f"Falha ao consultar o Redis para '{chave}': {err}")

            current_app.logger.info(f"Cache MISS: Consultado banco de dados PostgreSQL para '{chave}'.")
            response = func(*args, **kwargs)

            resp_obj = response[0] if isinstance(response, tuple) else response
            status = response[1] if isinstance(response, tuple) else resp_obj.status_code

            if status == 200:
                try:
                    payload = resp_obj.get_json()
                    redis_client.set(chave, json.dumps(payload), ex=ttl)
                except Exception as err:
                    current_app.logger.info(f"Falha ao salvar cache no Redis para '{chave}': {err}")
            return response
        return wrapper
    return decorator