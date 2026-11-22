from marshmallow import Schema, fields, validate, validates_schema, ValidationError
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
    preco_base = fields.Decimal(
        as_string=True,
        required=True,
        validate=validate.Range(
            min=Decimal('0.01'),
            error="O preco_base deve ser maior que zero.",
        ),
        error_messages={"required": "O campo 'preco_base' é obrigatório."}
    )
    preco_maximo = fields.Decimal(
        allow_none=True,
        as_string=True,
        required=False,
        validate=validate.Range(
            min=Decimal('0.01'),
            error="O preco_maximo deve ser maior que zero."
        ),
    )
    observacao = fields.String(
        allow_none=True,
        required=False,
        validate=validate.Length(min=2),
    )

    @validates_schema
    def validar_faixa_preco(self, data, **kwargs):
        preco_base = data.get('preco_base')
        preco_maximo = data.get('preco_maximo')

        if preco_maximo is not None and preco_base is not None:
            if preco_maximo <= preco_base:
                raise ValidationError(
                    "O preco máximo deve ser maior que o preço base.",
                    field_name="preco_maximo"
                )