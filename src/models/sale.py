import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base 

class Sale(Base):
    __tablename__ = "sales"

    # init=False: O ID é gerado pelo default (lambda) na hora do flush
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()), init=False)
    
    # CORREÇÃO CRÍTICA AQUI: init=False
    # Isso impede que o Python use a função 'datetime.now' como valor literal.
    # O SQLAlchemy vai executar essa função apenas na hora de salvar no banco.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, init=False)
    
    # init=False: Começa com 0 e calculamos depois no service
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, init=False)

    # init=False: Lista vazia gerenciada pelo ORM
    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale", 
        cascade="all, delete-orphan",
        default_factory=list,
        init=False 
    )

class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    
    # init=False: O SQLAlchemy preenche automaticamente ao adicionar na lista 'items' da venda
    sale_id: Mapped[str] = mapped_column(ForeignKey("sales.id"), init=False)
    
    # Estes são os ÚNICOS campos que passamos manualmente no código
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    sale: Mapped["Sale"] = relationship(back_populates="items", init=False)
    from src.models.product import Product
    product: Mapped["Product"] = relationship(init=False)