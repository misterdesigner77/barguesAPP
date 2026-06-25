from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (Integer, ForeignKey, Numeric, Enum, DateTime, String, Boolean)
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as OSEnum

# -- Types -----------
class Tipo(str, OSEnum):
    SANGRIA = "sangria"
    REGISTRO = "registro"
    ADICIONAR = "adicionar"

# -- Base -----------

class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    criacao: Mapped[date] = mapped_column(DateTime, default=datetime.now)
    modificado: Mapped[date] = mapped_column(DateTime, default=datetime.now)

# -- Caixa -----------

class Operacao(Base):
    __tablename__ = "operacoes"

    tipo: Mapped[Tipo] = mapped_column(Enum(Tipo, native_enum=False))
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    caixa_momento: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    correcao: Mapped["Correcao"] = relationship(back_populates="operacao")
class Correcao(Base):
    __tablename__ = "correcoes"

    valor: Mapped[Decimal] = mapped_column(Numeric(10,2))
    motivo: Mapped[str | None] = mapped_column(String(255), nullable= True)
    operacao_id: Mapped[int] = mapped_column(ForeignKey("operacoes.id"))

    operacao: Mapped["Operacao"] = relationship(back_populates="correcao")
# -- Estoque -----------

class Drinks(Base):
    __tablename__ = "drinks"

    nome: Mapped[str] = mapped_column(String(120))
    ativo: Mapped[bool] = mapped_column(Boolean)

    valores_drinks: Mapped[list["Valor"]] = relationship(foreign_keys="Valor.drink_id", back_populates="drink")


class Categoria(Base):
    __tablename__ = "categorias"

    nome: Mapped[str] = mapped_column(String(120))
    ativo: Mapped[bool] = mapped_column(Boolean)

    itens: Mapped[list["Item"]] = relationship(back_populates="categoria", foreign_keys="Item.categoria_id")
    valores_categoria: Mapped[list["Valor"]] = relationship(foreign_keys="Valor.categoria_id", back_populates="categoria")


class Item(Base):
    __tablename__ = "itens"

    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    nome: Mapped[str] = mapped_column(String(120))
    quantidade_recomendada: Mapped[int] = mapped_column(Integer)
    ativo: Mapped[bool] = mapped_column(Boolean)

    categoria: Mapped["Categoria"] = relationship(foreign_keys=[categoria_id],back_populates="itens")
    valores_item: Mapped[list["Valor"]] = relationship(foreign_keys="Valor.item_id", back_populates="item")
    media_consumo: Mapped["MediaConsumo"] = relationship(foreign_keys="MediaConsumo.item_id", back_populates="item")
    quantidade_atual: Mapped["QuantidadeAtual"] = relationship(foreign_keys="QuantidadeAtual.item_id", back_populates="item")


class Valor(Base):
    __tablename__ = "valores"

    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    drink_id: Mapped[int] = mapped_column(ForeignKey("drinks.id"))
    item_id: Mapped[int | None] = mapped_column(ForeignKey("itens.id"), nullable=True)
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), nullable=True)

    drink: Mapped["Drinks"] = relationship(foreign_keys=[drink_id], back_populates="valores_drinks")
    item: Mapped["Item"] = relationship(foreign_keys=[item_id], back_populates="valores_item")
    categoria: Mapped["Categoria"] = relationship(foreign_keys=[categoria_id], back_populates="valores_categoria")


# -- Auxiliares -----------

class MediaConsumo(Base):
    __tablename__ = "media_consumo"

    item_id: Mapped[int] = mapped_column(ForeignKey("itens.id"))
    quantidade_acumulo: Mapped[int] = mapped_column(Integer)
    media: Mapped[int] = mapped_column(Integer)

    item: Mapped["Item"] = relationship(foreign_keys=[item_id], back_populates="media_consumo")


class QuantidadeAtual(Base):
    __tablename__ = "quantidade_atual"

    item_id: Mapped[int] = mapped_column(ForeignKey("itens.id"))
    quantidade_atual: Mapped[int] = mapped_column(Integer)

    item: Mapped["Item"] = relationship(foreign_keys=[item_id], back_populates="quantidade_atual")