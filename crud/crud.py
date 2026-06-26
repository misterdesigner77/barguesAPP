from database import session
from .helpers import *
from schemas import *
from models import *
from sqlalchemy.orm import Session
from logger import logger
from datetime import datetime

db = session()


# Overloaded
def get_all(db:Session, model) -> list:
    """Recebe um model e resgata suas informacoes no db"""
    # TODO Usando classe com bind entre txt e classe, eu posso fazer isso bem puro e generico, dica para refatorar

    if model == Operacao: return (db.query(Operacao).all())

    elif model == Correcao: return (db.query(Correcao).all())

    else:
        error =f"Model {model!r} invalido"
        logger.warning(error)
        raise ValueError(error)


def get_ultimo_model(db: Session, model):
    """resgata a ultima operacao no banco. Importante pois existe a redundancia voluntaria no ultimo arquivo apontando
    o valor do caixa naquele momento"""

    if model == Operacao:
        operacao = db.query(Operacao).order_by(Operacao.id.desc()).first()
        return operacao if operacao else None
    
    if model == Correcao:
        correcao = db.query(Correcao).order_by(Correcao.id.desc()).first()
        return correcao if correcao else None


def get_specific_model(db:Session, id:str, model):
    resultado = None
    if model == Operacao:
        resultado = db.query(Operacao).filter(Operacao.id == id).first()

    elif model == Correcao:
        resultado = db.query(Correcao).filter(Correcao.id == id).first()

    if resultado:
        return resultado
    logger.warning(f"Id de operacao invalido. ID: {id}")
    raise ValueError(f"Operacao nao encontrada. ID: {id}")


# Get info
def get_caixa_atual(db:Session):
    """busca a ultima operacao e ocorrencia, compara as criacoes e retorna o caixa mais atualizado"""
    return calc_ultima_ocorrencia(ultima_correcao=get_ultimo_model(db=db, model=Correcao), ultima_operacao=get_ultimo_model(db=db, model=Operacao))
    
def get_tipos_periodo(db:Session, tipo:Tipo, data_inicial:date, data_final:date | None): 
    '''retorna todos os tipos no periodo indicado'''
    if not data_final:
        data_final = datetime.now()

    return db.query(Operacao).filter(Operacao.tipo == tipo).filter(Operacao.criacao >= data_inicial).filter(Operacao.criacao <= data_final).all()


# Operacoes
def create_operacoes(db: Session, data:OperacaoInput) -> Operacao:
    '''saves the operacoes in the db'''
    caixa = get_caixa_atual(db=db)
    caixa_atual = caixa + data.valor

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


# Correcoes
def create_correcao(db:Session, data:CorrecaoInput) -> Correcao:
    '''Cria uma correcao que se associa com uma operacao para realizar uma "edicao" em um valor introduzido anteriormente'''
    caixa = get_caixa_atual(db=db)
    caixa_atual = caixa + data.valor

    obj = Correcao(
        motivo=data.motivo,
        operacao_id=data.operacao_id,
        valor=data.valor,
        caixa_momento=caixa_atual
    )

    try:
        db.add(obj)
        db.commit()
        logger.info(f"Correcao realizada - ID:{obj.id}")
        return obj
    except Exception:
        db.rollback()
        logger.exception(f"Falha na correcao - ID:{obj.id}")
        raise


