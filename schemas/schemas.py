from pydantic import BaseModel as bm
from models.models import Tipo
from datetime import date
from decimal import Decimal

# -- Operacao ---------

class OperacaoBase(bm):
    valor: Decimal # Validar nao positivo
    tipo: Tipo


class OperacaoInput(OperacaoBase):
    pass


class OperacaoOutput(OperacaoBase):
    id: int
    criacao: date
    modificado: date
    caixa_momento: Decimal


class OperacaoEdit(bm):
    valor: Decimal | None = None 
    tipo: Tipo | None = None


# -- Correcao ---------

class CorrecaoBase(bm):
    motivo: str
    valor: Decimal
    operacao_id: int

class CorrecaoInput(CorrecaoBase):
    pass

class CorrecaoOutput(CorrecaoBase):
    id: int
    criacao: date

class CorrecaoEdit(bm):
    motivo: str | None = None
    valor: Decimal | None = None
    operacao_id: int | None = None

# -- Drinks ---------

class DrinkCategoriaBase(bm):
    nome: str


class DrinkInput(DrinkCategoriaBase):
    pass


class DrinkOutput(DrinkCategoriaBase):
    id: int
    ativo: bool
    criacao: date
    modificado: date

class DrinkEdit(bm):
    ativo: bool | None = None
    nome: str | None = None


# -- Categoria ---------

class CategoriaInput(DrinkCategoriaBase):
    pass


class CategoriaOutput(DrinkCategoriaBase):
    id: int
    criacao: date
    modificado: date
    ativo: bool

class CategoriaEdit(bm):
    ativo: bool | None = None
    nome: str | None = None


# -- Item ---------

class ItemBase(bm):
    nome: str
    categoria_id: int
    quantidade_recomendada: int


class ItemInput(ItemBase):
    pass


class ItemOutput(ItemBase):
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

class ValorBase(bm):
    valor: int 
    drink_id: int | None
    item_id: int | None
    categoria_id: int | None


class ValorInput(ValorBase):
    pass


class ValorOutput(ValorBase):
    id: int
    criacao: date
    modificado: date

class ValorEdit(bm):
    valor: int | None = None
    drink_id: int | None = None
    item_id: int | None = None
    categoria_id: int | None = None

# -- Media ---------

class MediaBse(bm):
    item_id: int
    quantidade_acumulo: int
    media: int


class MediaInput(MediaBse):
    pass


class MediaOutput(MediaBse):
    id: int
    atualizado_em: date


class MediaEdit(bm):
    item_id: int | None = None
    quantidade_acumulo: int | None = None
    media: int | None = None


# -- Qyabtudade Atual ---------

class QuantidadeBase(bm):
    item_id: int
    quantidade_atual: int


class QuantidadeInput(QuantidadeBase):
    pass


class QuantidadeOutput(QuantidadeBase):
    id: int
    criacao: date


class QuantidadeEdit(bm):
    item_id: int | None = None
    quantidade_atual: int | None = None