from app.models.database import db
from decimal import Decimal
from sqlalchemy.orm import validates

class Servico(db.Model):
    __tablename__ = 'servicos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    grupo = db.Column(db.String(100), nullable=False)
    preco_base = db.Column(db.Numeric(10, 2), nullable=False)
    preco_maximo = db.Column(db.Numeric(10, 2), nullable=True)
    observacao = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Servico {self.nome} - Grupo {self.grupo}>"

    @validates('preco_base')
    def validar_preco_base(self, key, valor):
        valor_decimal_base = Decimal(str(valor))

        if valor_decimal_base <= Decimal('0'):
            raise ValueError("O preço deve ser maior que zero")

        if self.preco_maximo is not None and valor_decimal_base > Decimal(str(self.preco_maximo)):
            raise ValueError("O preço base não pode ser maior que o 'preco_maximo'")

        return valor_decimal_base

    @validates('preco_maximo')
    def validar_preco_maximo(self, key, valor):
        if valor is None:
            return None
        
        valor_decimal_maximo = Decimal(str(valor))

        if valor_decimal_maximo <= Decimal('0'):
            raise ValueError("O preço deve ser maior que zero")
        
        if self.preco_base is not None and valor_decimal_maximo < Decimal(str(self.preco_base)):
            raise ValueError("O preço máximo não pode ser menor que o 'preco_base'")
        return valor_decimal_maximo