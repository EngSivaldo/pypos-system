# Definição da classe Product (Tabela products)
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class Product(Base):
    __tablename__ = "products"

    # Mapped[...] é a nova sintaxe do SQLAlchemy 2.0 (Totalmente tipada)
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    # unique=True garante que o banco rejeite dois produtos com mesmo código
    barcode: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    
    name: Mapped[str] = mapped_column(String(100))
    
    # Numeric(10, 2) = Até 10 digitos, sendo 2 decimais (ex: 99999999.99)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Product(name={self.name}, stock={self.stock_quantity})>"