from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, unset_access_cookies
from app.models.database import db
from app.core.logging_config import configure_logging
from app.core.swagger_config import init_swagger
from app.decorators import register_jwt_handlers

jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask("Taciana Lanhouse")
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)
    register_jwt_handlers(jwt)

    from app.models import categoria, produto, usuario
    migrate.init_app(app, db)

    configure_logging(app)
    init_swagger(app)

    from app.routes.categorias import categorias_bp
    from app.routes.produtos import produtos_bp
    from app.routes.usuarios import usuarios_bp

    app.register_blueprint(categorias_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(usuarios_bp)

    return app