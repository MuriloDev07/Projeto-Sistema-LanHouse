from marshmallow import Schema, fields, validate
from decimal import Decimal

class CategoriaSchema(Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str(
        required=True,
        validate=validate.Length(min=2),
        error_messages={"required": "O campo 'nome' é obrigatório."}
    )

class ProdutoSchema(Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str(
        required=True,
        validate=validate.Length(min=2),
        error_messages={"required":" O campo 'nome' é obrigatório."}
    )
    preco = fields.Decimal(
        as_string=True,
        required=True,
        validate=validate.Range(
            min=Decimal("0.01"),
            error="O preço deve ser maior que zero."
        ),
        error_messages={"required": "O campo 'preco' é obrigatório."}
    )
    quantidade = fields.Int(
        required=True,
        validate=validate.Range(
            min=0,
            error="A quantidade não pode ser negativa."
        ),
        error_messages={"required": "O campo 'quantidade' é obrigatório."}
    )
    categoria_id = fields.Int(
        required=True,
        error_messages={"required": "O ID da categoria é obrigatório."}
    )

class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.String(
        required=True,
        validate=validate.Length(min=2),
        error_messages={"required": "O campo 'usuario' é obrigatório."}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6),
        load_only=True,
        error_messages={"required": "O campo 'senha' é obrigatório."}
    )
    role = fields.String(dump_only=True)

class ServicoSchema(Schema):
    id = fields.Int(dump_only=True)
    nome = fields.String(
        required=True,
        validate=validate.Length(min=2),
        error_messages={"required": "O campo 'nome' é obrigatório."}
    )
    grupo = fields.String(
        required=True,
        validate=validate.Length(min=2),
        error_messages={"required": "O campo 'grupo' é obrigatório."}
    )
    preco = fields.Decimal(
        as_string=True,
        required=True,
        validate=validate.Range(
            min=Decimal('0.01'),
            error="O preco deve ser maior que zero.",
        ),
        error_messages={"required": "O campo 'preco' é obrigatório."}
    )
    observacao = fields.String(
        allow_none=True,
        required=False,
        validate=validate.Length(min=2),
    )