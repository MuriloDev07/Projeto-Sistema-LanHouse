import pytest
from app import create_app
from app.models.database import db
from app.models.usuario import Usuario
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    _app = create_app()
    _app.config['TESTING'] = True
    _app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    _app.config['JWT_CONFIG_KEY'] = 'chave-secreta-de-testes-automatizados-123'
    return _app

@pytest.fixture
def client(app):
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
def usuario_admin(app):
    with app.app_context():
        usuario = Usuario(username="admin_teste", role= "admin")
        usuario.set_password("senha_segura_123")
        db.session.add(usuario)
        db.session.commit()
        return usuario
    
@pytest.fixture
def admin_auth_headers(app):
    with app.app_context():
        token = create_access_token(
            identity="1",
            additional_claims={"role": "admin"}
        )
        return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user_auth_headers(app):
    with app.app_context():
        token = create_access_token(
            identity="2",
            additional_claims={"role": "user"}
        )
        return {"Authorization": f"Bearer {token}"}