from crud import *
from schemas import *
from models import *


# -- Operacoes ----------

def test_get_ultima_operacao_vazio(db):
    result = get_ultima_operacao(db=db)
    assert result is None


def test_get_all_vazio(db):
    resultado = get_all(db)
    assert resultado == []


def test_get_all_com_dados(db):
    operacao = create_operacoes(db=db, data=OperacaoInput(
        valor=50,
        tipo="sangria"
        ))
    resultado = get_all(db)
    assert len(resultado) == 1 


def test_get_especifico(db):
    operacao = create_operacoes(db=db, data=OperacaoInput(
        valor=50,
        tipo="sangria"
        ))
    resultado = get_specific(db=db, id=1)
    assert resultado.valor == 50


def test_create_operacoes(db):    
    operacao = create_operacoes(db=db, data=OperacaoInput(
        valor=50,
        tipo="sangria"
        ))
    assert operacao.valor == Decimal(50)
    assert operacao.tipo == Tipo.SANGRIA


def test_edit_operacao(db):
    create_operacoes(db=db, data=OperacaoInput(
        valor=50,
        tipo=Tipo.SANGRIA
        ))
    editado = edit_operacao(db=db, data=OperacaoEdit(
        valor=150,
        tipo= Tipo.REGISTRO
    ), id=1)
    assert editado.valor == 150
    assert editado.tipo == Tipo.REGISTRO