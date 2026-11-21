from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, unset_access_cookies
from app.models.database import db
from app.core.logging_config import configure_logging
from app.core.swagger_config import init_swagger
from app.decorators import register_jwt_handlers
from flask_cors import CORS

jwt = JWTManager()
migrate = Migrate()
cors = CORS()

def create_app():
    app = Flask("Taciana Lanhouse")
    app.config.from_object('config.Config')

    cors.init_app(
        app,
        origins=['http://127.0.0.1:3000', 'http://localhost:3000'],
        supports_credentials=True
    )

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