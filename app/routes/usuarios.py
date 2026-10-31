from flask import Blueprint, request, jsonify
from app.models.database import db
from app.models.usuario import Usuario
from app.models.schemas import UsuarioSchema
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/auth')
usuario_schema = UsuarioSchema()

@usuarios_bp.route('/registro', methods=['POST'])
def registrar():
    dados = request.get_json()

    try:
        dados_validados = usuario_schema.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if Usuario.query.filter_by(username=dados_validados['username']).first():
        return jsonify({"erro": "Usuário já cadastrado"}), 400

    novo_usuario = Usuario(username=dados_validados['username'])
    novo_usuario.set_password(dados_validados['password'])

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify(usuario_schema.dump(novo_usuario)), 201

@usuarios_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()

    try:
        dados_validados = usuario_schema.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400

    usuario = Usuario.query.filter_by(username=dados_validados['username']).first()
 
    if not usuario and not usuario.check_password(dados_validados['password']):
        return jsonify({"erro":"Credenciais inválidadas"}), 401

    token = create_access_token(identity=str(usuario.id))
    return jsonify({"acess_token": token}), 200