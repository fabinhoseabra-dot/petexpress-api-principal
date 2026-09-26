from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PedidoCreate(BaseModel):
    nome_cliente: str
    cep: str
    numero: str
    complemento: str | None = None
    descricao_pedido: str


class PedidoUpdate(BaseModel):
    nome_cliente: str | None = None
    numero: str | None = None
    complemento: str | None = None
    descricao_pedido: str | None = None
    status: str | None = None


class PedidoResponse(BaseModel):
    id: int
    nome_cliente: str
    cep: str
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cidade: str
    uf: str
    descricao_pedido: str
    status: str
    valor_frete: float
    prazo_entrega: int
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)