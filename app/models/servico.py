from app.models.database import db
from decimal import Decimal
from sqlalchemy.orm import validates

class Servico(db.Model):
    __tablename__ = 'servicos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    grupo = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    observacao = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Servico {self.nome} - Grupo {self.grupo}>"

    @validates('preco')
    def validar_preco(self, key, valor):
        valor_decimal = Decimal(str(valor))
        if valor_decimal <= Decimal('0'):
            raise ValueError("O preço deve ser maior que zero")
        return valor_decimal