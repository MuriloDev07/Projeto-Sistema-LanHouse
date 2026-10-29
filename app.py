import os
from flask import Flask
from flask_migrate import Migrate
from models.database import db

app = Flask("Taciana Lanhouse")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

from models.categoria import Categoria
from models.produto import Produto
from routes.categorias import categorias_bp
from routes.produtos import produtos_bp

app.register_blueprint(categorias_bp)
app.register_blueprint(produtos_bp)

if __name__ == "__main__":
    app.run(debug=True)