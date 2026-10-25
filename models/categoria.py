from models.database import db
from flask import jsonify

class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Categoria {self.nome}>"

    @staticmethod
    def validar(dados):
        if not dados:
             return jsonify({"erro": "Nenhum dado fornecido"}), 400
        if 'nome' not in dados:
            return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400
        if not dados['nome'] or not isinstance(dados['nome'], str):
            return jsonify({"erro": "Nome inválido"}), 400
        return True
        