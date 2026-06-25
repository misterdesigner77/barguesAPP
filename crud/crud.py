from database import session
from schemas import *
from models import *
from sqlalchemy.orm import Session
from logger import logger
from datetime import datetime

db = session()

# Operacoes

def get_ultima_operacao(db: Session) -> Operacao:
    """resgata a ultima operacao no banco. Importante pois existe a redundancia voluntaria no ultimo arquivo apontando
    o valor do caixa naquele momento"""
    operacao = db.query(Operacao).order_by(Operacao.id.desc()).first()
    return operacao if operacao else None


def get_all(db:Session) -> list:
    return (db.query(Operacao).all())


def get_specific(db:Session, id:str) -> Operacao:
    resultado = db.query(Operacao).filter(Operacao.id == id).first()
    if resultado:
        return resultado
    logger.warning(f"Id de operacao invalido. ID: {id}")
    raise ValueError(f"Operacao nao encontrada. ID: {id}")


def create_operacoes(db: Session, data:OperacaoInput) -> Operacao:
    '''saves the operacoes in the db'''
    caixa_atual = get_ultima_operacao(db=db)
    caixa_atual = caixa_atual.caixa_momento if caixa_atual else Decimal(0)

    if data.tipo == Tipo.SANGRIA:
        caixa_atual -= data.valor
    elif data.tipo == Tipo.REGISTRO or data.tipo == Tipo.ADICIONAR:
        caixa_atual += data.valor

    obj = Operacao(
        valor=data.valor,
        caixa_momento=caixa_atual,
        tipo=data.tipo
    )
    
    try:
        db.add(obj)
        db.commit()
        logger.info(f"Operacao registrada com sucesso - ID:{obj.id}")
        return obj
    except Exception:
        db.rollback()
        logger.exception("Erro na criacao da operaçao")
        raise


def edit_operacao(db:Session, id:int, data:OperacaoEdit) -> Operacao:
    '''edita valor ou tipo da operacao e atualiza o modificado e o caixa salvo'''
    obj = db.query(Operacao).filter(Operacao.id == id).first()
    if not obj:
        logger.warning(f"Operacao nao encontrada")
        raise ValueError("Operacao nao encontrada")
    
    if data.valor:
        dif_caixa = obj.valor - data.valor
        obj.caixa_momento += dif_caixa

    for value, key in data.model_dump(exclude_none=True).items():
        setattr(obj, value, key)

    obj.modificado = datetime.now()
    print(f"TESTE: {obj.__dict__}")

    try:
        db.commit()
        logger.info(f"Operacao editada - ID:{obj.id}")
        return obj
    except Exception:
        db.rollback()
        logger.exception(f"Falha na edicao - ID:{obj.id}")
        raise



