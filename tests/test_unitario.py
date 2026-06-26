from crud import *
from schemas import *
from models import *


# -- Operacoes ----------

def test_db_vazio(db):
    # Ultima operacao
    result = get_ultimo_model(db=db, model=Operacao)
    assert result is None

    # Todas correcoes
    resultado = get_all(db=db, model=Correcao)
    assert resultado == []



def test_com_data(db):
    # Criar um registro de operacao
    create_operacoes(db=db, data=OperacaoInput(
        valor=50,
        tipo="sangria"
        ))
    resultado = get_all(db, model=Operacao)
    assert len(resultado) == 1 

    # Resgatar uma operacao em especifico
    resultado = get_specific_model(db=db, id=1, model=Operacao)
    assert resultado.valor == 50

    # Criar correcao
    correcao = create_correcao(db=db, data=CorrecaoInput(
        valor=10,
        motivo="Erro de valor",
        operacao_id=1
        ))
    assert correcao.valor == Decimal(10)

    # Resgata ultima correcao
    resultado = get_ultimo_model(db=db, model=Correcao)
    assert resultado.valor == Decimal(10)

    # Busca o mais recente
    caixa = get_caixa_atual(db=db)
    assert caixa == Decimal(10)