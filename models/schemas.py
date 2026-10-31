from marshmallow import Schema, fields, validate

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
    preco = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"erro": "O preco não pode ser negativo."}
    )
    quantidade = fields.Int(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"erro": "A quantidade não pode ser negativa."}
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