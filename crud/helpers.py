from decimal import Decimal
from models import *



def calc_ultima_ocorrencia(ultima_operacao:Operacao, ultima_correcao:Correcao) -> Decimal:
    """Nunca retorna None, sempre retorna Decimal"""
    if ultima_correcao and not ultima_operacao: return ultima_correcao.caixa_momento
    elif ultima_operacao and not ultima_correcao: return ultima_operacao.caixa_momento
    elif not ultima_operacao and not ultima_correcao: return Decimal(0)


    mais_recente = max(ultima_operacao.criacao, ultima_correcao.criacao)

    if mais_recente == ultima_operacao.criacao: return ultima_operacao.caixa_momento
    return ultima_correcao.caixa_momento

def modelo_caixa():
    return {
        valor_dinheiro:str,
    }