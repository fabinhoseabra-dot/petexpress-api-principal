import os

import requests
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app import models
from app.schemas import PedidoCreate, PedidoUpdate, PedidoResponse


Base.metadata.create_all(bind=engine)


LOGISTICA_URL = os.getenv(
    "LOGISTICA_URL",
    "http://127.0.0.1:8001"
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def consultar_logistica(cep: str) -> dict:
    try:
        resposta = requests.post(
            f"{LOGISTICA_URL}/frete",
            json={"cep": cep},
            timeout=10
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API de Logística indisponível."
        )

    if resposta.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CEP não encontrado."
        )

    if resposta.status_code == 422:
        detalhe = resposta.json().get(
            "detail",
            "Região não atendida."
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detalhe
        )

    if not resposta.ok:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao consultar a API de Logística."
        )

    return resposta.json()


app = FastAPI(
    title="PetExpress - API Principal",
    description="API responsável pela gestão de pedidos e entregas do PetExpress.",
    version="1.0.0"
)


@app.get("/health", tags=["Sistema"])
def health_check():
    return {
        "status": "online",
        "service": "PetExpress API Principal"
    }


@app.get(
    "/pedidos",
    response_model=list[PedidoResponse],
    tags=["Pedidos"]
)
def listar_pedidos(
    status_pedido: str | None = None,
    db: Session = Depends(get_db)
):
    consulta = db.query(models.Pedido)

    if status_pedido:
        consulta = consulta.filter(
            models.Pedido.status == status_pedido
        )

    return consulta.all()


@app.post(
    "/pedidos",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Pedidos"]
)
def criar_pedido(
    pedido: PedidoCreate,
    db: Session = Depends(get_db)
):
    logistica = consultar_logistica(pedido.cep)

    novo_pedido = models.Pedido(
        nome_cliente=pedido.nome_cliente,
        cep=logistica["cep"],
        logradouro=logistica["logradouro"],
        numero=pedido.numero,
        complemento=pedido.complemento,
        bairro=logistica["bairro"],
        cidade=logistica["cidade"],
        uf=logistica["uf"],
        descricao_pedido=pedido.descricao_pedido,
        status="pendente",
        valor_frete=logistica["valor_frete"],
        prazo_entrega=logistica["prazo_entrega"]
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    return novo_pedido


@app.patch(
    "/pedidos/{pedido_id}",
    response_model=PedidoResponse,
    tags=["Pedidos"]
)
def atualizar_pedido(
    pedido_id: int,
    dados: PedidoUpdate,
    db: Session = Depends(get_db)
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado"
        )

    dados_atualizacao = dados.model_dump(exclude_unset=True)

    for campo, valor in dados_atualizacao.items():
        setattr(pedido, campo, valor)

    db.commit()
    db.refresh(pedido)

    return pedido


@app.delete(
    "/pedidos/{pedido_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Pedidos"]
)
def excluir_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()

    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado"
        )

    db.delete(pedido)
    db.commit()

    return None