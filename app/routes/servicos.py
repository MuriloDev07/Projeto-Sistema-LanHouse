from flasgger import swag_from
from flask import Blueprint, jsonify, request, current_app
from app.models.database import db, atomic_transaction
from app.models.servico import Servico
from app.models.schemas import ServicoSchema
from marshmallow import ValidationError
from app.decorators import admin_required, cache_aside, invalidate_cache

servicos_bp = Blueprint('servicos', __name__, url_prefix='/servicos')

servico_schema = ServicoSchema()
servicos_schema = ServicoSchema(many=True)

CACHE_KEY_SERVICOS = 'servicos:all'

@servicos_bp.route('', methods=['GET'])
@cache_aside(CACHE_KEY_SERVICOS)
@swag_from("../docs/servicos/get_servicos.yml")
def get_servicos():
    servicos = Servico.query.all()
    resultado = servicos_schema.dump(servicos)
    return jsonify(mensagem="Lista de Servicos (Banco)", servicos=resultado)

@servicos_bp.route('/<int:servico_id>', methods=['GET'])
@swag_from("../docs/servicos/get_servico_por_id.yml")
def get_servico_por_id(servico_id):
    servico = db.session.get(Servico, servico_id)

    if servico:
        return jsonify(servico_schema.dump(servico))
    current_app.logger.warning(f"Busca de servicos falhou: ID {servico_id} não encontrado")
    return jsonify({"erro": "Servico não encontrado"}), 404

@servicos_bp.route('', methods=['POST'])
@admin_required()
@invalidate_cache(CACHE_KEY_SERVICOS)
@swag_from('../docs/servicos/create_servico.yml')
def create_servico():
    dados = request.get_json()

    try:
        dados_validados = servico_schema.load(dados)
    except ValidationError as err:
        current_app.logger.warning(f"Falha de validação ao criar servico: {err.messages}")
        return jsonify(err.messages), 400

    if Servico.query.filter_by(nome=dados_validados['nome']).first():
        current_app.logger.warning(f"Tentantiva de criar servico duplicado: '{dados_validados['nome']}'")
        return jsonify({"erro": "Servico já cadastrado"}), 400

    novo_servico = Servico(
        nome=dados_validados['nome'],
        grupo=dados_validados['grupo'],
        preco=dados_validados['preco'],
        observacao = dados_validados.get('observacao')
    )

    with atomic_transaction():
        db.session.add(novo_servico)

    current_app.logger.info(f"Servico '{novo_servico.nome}' (ID: {novo_servico.id}) criado com sucesso no PostgreSQL")
    
    return servico_schema.dump(novo_servico), 201

@servicos_bp.route('/<int:servico_id>', methods=['DELETE'])
@admin_required()
@invalidate_cache(CACHE_KEY_SERVICOS)
@swag_from("../docs/servicos/remove_servico.yml")
def remove_servico(servico_id):
    servico = db.session.get(Servico, servico_id)

    if servico is None:
        current_app.logger.warning(f"Tentativa de exclusão falha: Servico ID {servico_id} não existe")
        return jsonify({"erro": "Servico não encontrado"}), 404

    with atomic_transaction():
        db.session.delete(servico)

    current_app.logger.info(f"Servico '{servico.nome}' (ID: {servico_id} removido com sucesso do PostgreSQL)")

    return jsonify({"mensagem": "Servico removido com sucesso"}), 200

@servicos_bp.route('/<int:servico_id>', methods=['PUT'])
@admin_required()
@invalidate_cache(CACHE_KEY_SERVICOS)
@swag_from("../docs/servicos/update_servico.yml")
def update_servico(servico_id):
    dados = request.get_json()
    servico = db.session.get(Servico, servico_id)

    if servico is None:
        current_app.logger.warning(f"Tentativa de atualização falha: Servico ID {servico_id}")
        return jsonify({"erro": "Servico não encontrado"}), 404

    try:
        dados_validados = servico_schema.load(dados)
    except ValidationError as err:
        current_app.logger.error(f"Falha na validação ao atualizar Servico ID {servico_id}: {err.messages}")
        return jsonify(err.messages), 400

    existente = Servico.query.filter_by(nome=dados_validados['nome']).first()
    if existente and existente.id != servico_id:
        return jsonify({"erro": "Já existe outro serviço com este nome"}), 400

    with atomic_transaction():
        nome_antigo = servico.nome
        servico.nome = dados_validados['nome']
        servico.grupo = dados_validados['grupo']
        servico.preco = dados_validados['preco']
        servico.observacao = dados_validados.get('observacao')

    current_app.logger.info(f"Servico ID {servico_id} atualizado: '{nome_antigo}' -> {servico.nome}")

    return jsonify(mensagem="Servico atualizado com sucesso", servico=servico_schema.dump(servico))