from models.database import db
from flask import jsonify

class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Produto {self.nome} - Qtd: {self.quantidade}>"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "preco": self.preco,
            "quantidade": self.quantidade,
            "categoria_id": self.categoria_id
        }

    @staticmethod
    def validar(dados):
        if not dados:
            return jsonify({"erro": "Nenhum dado fornecido"}), 400

        if 'nome' not in dados:
            return jsonify({"erro": "campo 'nome' é obrigatório"}), 400

        if not dados['nome'] or not isinstance(dados['nome'], str):
            return jsonify({"erro": "Nome Inválido"}), 400
        
        if 'preco' not in dados:
            return jsonify({"erro": "campo 'preco' é obrigatório"}), 400

        try:
            real = float(dados['preco'])
        except ValueError:
            return jsonify({"erro": "preco inválido"}), 400
        else:
            if real < 0:
                return jsonify({"erro": "o preco não pode ser negativo"}), 400
            dados['preco'] = real

        if 'quantidade' not in dados:
            return jsonify({"erro": "campo 'quantidade' é obrigatório"}), 400

        try:
            inteiro = int(dados['quantidade'])
        except ValueError:
            return jsonify({"erro": "quantidade inválida"}), 400
        else:
            if inteiro < 0:
                return jsonify({"erro": "a quantidade não pode ser negativa"}), 400
            dados['quantidade'] = inteiro

        return True