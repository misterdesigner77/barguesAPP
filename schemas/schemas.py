from pydantic import BaseModel as bm
from models.models import Tipo
from datetime import date
from decimal import Decimal

# -- Operacao ---------
class OperacaoInput(bm):
    valor: Decimal # Validar nao positivo
    tipo: Tipo


class OperacaoOutput(OperacaoInput):
    id: int
    criacao: date
    modificado: date
    caixa_momento: Decimal

# -- Correcao ---------
class CorrecaoInput(bm):
    motivo: str | None = None
    valor: Decimal
    operacao_id: int


class CorrecaoOutput(CorrecaoInput):
    id: int
    criacao: date

# -- Caixa ---------
class CaixaInput(bm):
    valor_cartao:Decimal
    total_sistema:Decimal
    cartao_sistema:Decimal


class CaixaOutput(CaixaInput): 
    criacao:date
    valor_dinheiro:Decimal
    sangria:Decimal
    

class RelatorioCaixa(bm):
    dias_registrados: int
    total_sistema: Decimal
    cartao_sistema: Decimal
    dinheiro_sistema: Decimal
    valor_dinheiro_bruto: Decimal
    valor_dinheiro_liquido: Decimal # Subtrai com o caixa antigo
    valor_cartao: Decimal
    sangria_total: Decimal
    caixa_antigo: Decimal

# -- Drinks ---------
class DrinkCategoriaOutput(bm):
    id: int
    ativo: bool
    criacao: date
    modificado: date

class DrinkCategoriaInput(bm):
    nome: str


class DrinkCategoriaEdit(bm):
    ativo: bool | None = None
    nome: str | None = None

# -- Item ---------
class ItemInput(bm):
    nome: str
    categoria_id: int
    quantidade_recomendada: int


class ItemOutput(ItemInput):
    id: int
    ativo: bool
    criacao: date
    modificado: date


class ItemEdit(bm):
    nome: str | None = None
    categoria_id: int | None = None
    quantidade_recomendada: int | None = None
    ativo: bool | None = None

# -- Valor ---------
class ValorInput(bm):
    valor: int 
    drink_id: int | None
    item_id: int | None
    categoria_id: int | None


class ValorOutput(ValorInput):
    id: int
    criacao: date
    modificado: date


class ValorEdit(bm):
    valor: int | None = None
    drink_id: int | None = None
    item_id: int | None = None
    categoria_id: int | None = None

# -- Media ---------
class MediaInput(bm):
    item_id: int
    quantidade_acumulo: int
    media: int


class MediaOutput(MediaInput):
    id: int
    atualizado_em: date


class MediaEdit(bm):
    item_id: int | None = None
    quantidade_acumulo: int | None = None
    media: int | None = None


# -- Quantidade Atual ---------
class QuantidadeInput(bm):
    item_id: int
    quantidade_atual: int


class QuantidadeOutput(QuantidadeInput):
    id: int
    criacao: date


class QuantidadeEdit(bm):
    item_id: int | None = None
    quantidade_atual: int | None = None