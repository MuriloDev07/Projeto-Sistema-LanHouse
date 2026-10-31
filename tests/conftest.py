import pytest
from app import create_app
from app.models.database import db
from flask_jwt_extended import create_access_token

app = create_app()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'chave-secreta-de-testes-automatizados-123'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_headers():
    with app.app_context():
        token = create_access_token(identity="1")

    return {"Authorization": f"Bearer {token}"}