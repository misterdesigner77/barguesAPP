from database import session
from .helpers import *
from schemas import *
from models import *
from sqlalchemy.orm import Session

from logger import logger
from datetime import datetime

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
    return calc_ultima_ocorrencia(ultima_correcao=get_ultimo_model(db=db, model=Correcao),
                                  ultima_operacao=get_ultimo_model(db=db, model=Operacao))


def get_tipos_periodo(db:Session, tipo:Tipo, data_inicial:datetime, data_final:datetime | None=None): 
    '''retorna todos os tipos no periodo indicado'''
    if not data_final:
        data_final = datetime.now()

    resultados = db.query(Operacao).filter(Operacao.tipo == tipo).all()

    return [op for op in resultados if data_inicial.date() <= op.criacao.date() <= data_final.date()]


def get_fluxo_de_caixa(db:Session, data_inicial:datetime, data_final:datetime | None=None) -> list | None:
    """Busca o caixa do dia e retorna o caixa ou None"""
    if not data_final:
        data_final=datetime.now()

    caixa_diario = db.query(CaixaDiario).all()

    if caixa_diario:
        return [op for op in caixa_diario if data_inicial.date() <= op.criacao.date() <= data_final.date()]
    return None


def get_ultimo_caixa_fisico(db:Session, data_inicial:datetime) -> Decimal:
    resultado = db.query(Operacao).filter(Operacao.criacao < data_inicial.date()).order_by(
        Operacao.criacao.desc()).first() 
    return resultado.caixa_momento if resultado else Decimal(0)


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

# Caixa
def make_caixa(db:Session, data:CaixaInput) -> CaixaDiario:
    # reegistra o cartao no fluxo do caixa, pois somente se coleta uma vez por dia
    caixa = get_caixa_atual(db=db) + data.valor_cartao

    reg_cartao= Operacao(
        tipo=Tipo.CARTAO,
        valor=data.valor_cartao,
        caixa_momento=caixa
    )

    obj = CaixaDiario(
        cartao_sistema=data.cartao_sistema,
        sangria_total= sum(op for op in get_tipos_periodo(db=db, tipo=Tipo.SANGRIA, 
                                             data_inicial=datetime.now())),
        valor_cartao=reg_cartao.valor,
        total_sistema=data.total_sistema,
        valor_dinheiro= sum(op for op in get_tipos_periodo(db=db, tipo=Tipo.DINHEIRO, 
                                              data_inicial=datetime.now()))
    )

    try:
        db.add(obj)
        db.add(reg_cartao)
        db.commit()
        logger.info(f"Caixa registrado - ID:{obj.id}\nCartao Registrado: ID{reg_cartao.id}")
        return obj
    except Exception:
        db.rollback()
        logger.exception("Erro ao registrar caixa")
        raise

# Relatorio
def gerar_relatorio_caixa(db:Session, data_inicial:datetime,
                          data_final:datetime | None = None) -> RelatorioCaixa:
    caixas_periodos = get_fluxo_de_caixa(db=db, data_inicial=data_inicial,
                                         data_final=data_final)
    
    caixa_anterior = get_ultimo_caixa_fisico(db=db, data_inicial=data_inicial)

    return RelatorioCaixa(
        total_sistema=sum(caixa.total_sistema for caixa in caixas_periodos),
        cartao_sistema=sum(caixa.cartao_sistema for caixa in caixas_periodos),
        dinheiro_sistema=sum(caixa.total_sistema for caixa in caixas_periodos) - sum(
            caixa.cartao_sistema for caixa in caixas_periodos),
        valor_dinheiro_bruto=sum(caixa.valor_dinheiro for caixa in caixas_periodos),
        valor_dinheiro_liquido=sum(caixa.valor_dinheiro for caixa in caixas_periodos) - caixa_anterior,
        valor_cartao=sum(caixa.valor_cartao for caixa in caixas_periodos),
        sangria_total=sum(caixa.sangria_total for caixa in caixas_periodos),
        dias_registrados=len(caixas_periodos),
        caixa_antigo=caixa_anterior
    )