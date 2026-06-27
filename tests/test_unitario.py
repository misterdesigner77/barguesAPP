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

    # Busca o de hoje
    resultado = get_tipos_periodo(db=db, tipo=Tipo.SANGRIA, data_inicial=datetime.now())
    print(f"teste: {resultado}")
    assert type(resultado) == list

def test_make_caixa(db):
    # Criar caixa
    caixa = make_caixa(db=db, data=CaixaInput(
        valor_cartao=400,
        total_sistema=1200,
        cartao_sistema=700,
    ))
    assert caixa.valor_dinheiro == 0
    assert caixa.total_sistema == 1200

    cartao = get_tipos_periodo(db=db, tipo=Tipo.CARTAO, data_inicial=datetime.now())
    assert sum(op.valor for op in cartao) == 400

    # Buscar caixa
    caixa = get_fluxo_de_caixa(db=db, data_inicial=datetime.now())
    assert caixa[0].valor_cartao == 400

    # Gerar relatorio
    relatorio = gerar_relatorio_caixa(db=db, data_inicial=datetime.now())
    print(relatorio)
    assert relatorio.dias_registrados == 1
    assert relatorio.total_sistema == 1200
    assert relatorio.dinheiro_sistema == 500