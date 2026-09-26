from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String, nullable=False)
    cep = Column(String, nullable=False)
    logradouro = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    complemento = Column(String, nullable=True)
    bairro = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    uf = Column(String, nullable=False)
    descricao_pedido = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pendente")
    valor_frete = Column(Float, nullable=False)
    prazo_entrega = Column(Integer, nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)