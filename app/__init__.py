from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, unset_access_cookies
from app.models.database import db

jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask("Taciana Lanhouse")
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)

    from app.models import categoria, produto, usuario
    migrate.init_app(app, db)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        response = jsonify({
            "erro": "token_expired",
            "mensagem": "Sua sessão expirou. Por favor, faça login novamente."
        })
        unset_access_cookies(response)
        return response, 401

    from app.routes.categorias import categorias_bp
    from app.routes.produtos import produtos_bp
    from app.routes.usuarios import usuarios_bp

    app.register_blueprint(categorias_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(usuarios_bp)

    return app