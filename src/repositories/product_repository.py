# Implementação do padrão Repository para Produtos.
# Aqui vão os métodos: add, get_by_code, update_stock, etc.
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from src.models.product import Product

class ProductRepository:
    """
    Responsável exclusivamente pelo acesso a dados da tabela 'products'.
    Não deve conter regras de negócio (ex: verificar se pode vender).
    Apenas executa ordens de banco de dados.
    """

    def __init__(self, session: Session):
        # Injeção de Dependência: O repositório precisa de uma sessão aberta para trabalhar
        self.session = session

    def add(self, product: Product) -> Product:
        """Salva um novo produto no banco."""
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product) # Atualiza o ID gerado pelo banco
        return product

    def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """Busca um produto exato pelo código de barras."""
        # SQLAlchemy 2.0: select(Modelo).where(Condição)
        stmt = select(Product).where(Product.barcode == barcode)
        
        # scalars().first() retorna o objeto puro ou None
        return self.session.execute(stmt).scalars().first()

    def get_all(self) -> List[Product]:
        """Retorna todos os produtos cadastrados."""
        stmt = select(Product).order_by(Product.name)
        return list(self.session.execute(stmt).scalars().all())

    def update_stock(self, product_id: int, new_quantity: int) -> None:
        """Atualiza apenas a quantidade de estoque de forma eficiente."""
        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(stock_quantity=new_quantity)
        )
        self.session.execute(stmt)
        self.session.commit()