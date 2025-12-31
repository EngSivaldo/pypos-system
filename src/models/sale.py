# Definição das classes Sale e SaleItem
from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import ForeignKey, Numeric, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base

class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    # Relacionamento com a Venda (Pai)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), init=False)
    
    # Relacionamento com o Produto
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    
    quantity: Mapped[int] = mapped_column()
    
    # SNAPSHOT DE PREÇO: O preço DO MOMENTO da venda.
    # Se o produto mudar de preço amanhã, este valor fica salvo para sempre.
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2))

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    # uuid garante que podemos sincronizar com outros sistemas no futuro sem conflito de ID
    uuid: Mapped[str] = mapped_column(String(36), unique=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    
    # Relacionamento One-to-Many: Uma venda tem vários itens
    # cascade="all, delete-orphan": Se deletar a venda, deleta os itens.
    items: Mapped[List["SaleItem"]] = relationship(
        "SaleItem", 
        backref="sale", 
        cascade="all, delete-orphan",
        default_factory=list
    )