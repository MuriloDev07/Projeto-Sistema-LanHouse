import os
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from models.database import db

app = Flask("Taciana Lanhouse")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

db.init_app(app)
migrate = Migrate(app, db)

from routes.categorias import categorias_bp
from routes.produtos import produtos_bp
from routes.usuarios import usuarios_bp

app.register_blueprint(categorias_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(usuarios_bp)

if __name__ == "__main__":
    app.run(debug=True)