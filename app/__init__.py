from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.models.database import db

jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask("Taciana Lanhouse")
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt.init_app(app)

    from app.models import categoria, produto, usuario
    migrate.init_app(app)

    from app.routes.categorias import categorias_bp
    from app.routes.produtos import produtos_bp
    from app.routes.usuarios import usuarios_bp

    app.register_blueprint(categorias_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(usuarios_bp)

    return app