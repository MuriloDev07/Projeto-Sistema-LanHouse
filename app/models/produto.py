from app.models.database import db
from decimal import Decimal
from sqlalchemy.orm import validates

class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10,2), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Produto {self.nome} - Qtd: {self.quantidade}>"

    @validates('preco')
    def validar_preco(self, key, valor):
        valor_decimal = Decimal(str(valor))
        if valor_decimal <= Decimal('0'):
            raise ValueError("O preço deve ser maior que zero")
        return valor_decimal

    @validates('quantidade')
    def validar_quantidade(self, key, valor):
        if valor < 0:
            raise ValueError("A quantidade não pode ser negativa")
        return valor

    @property
    def valor_total_estoque(self):
        return self.preco * self.quantidade