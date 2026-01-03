from typing import List, Optional
# IMPORTANTE: Adicionei 'delete' aqui no topo para não importar dentro da função
from sqlalchemy import select, update, delete
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
        stmt = select(Product).where(Product.barcode == barcode)
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

    # --- MÉTODO AJUSTADO PARA INCLUIR CATEGORIA ---
    def update(self, product_id: int, name: str, price: float, stock: int, category: str) -> None:
        """Atualiza os dados gerais de um produto existente, incluindo a categoria."""
        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(
                name=name,
                price=price,
                stock_quantity=stock,
                category=category # <--- AGORA O BANCO VAI SALVAR!
            )
        )
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, product_id: int) -> None:
        """Remove um produto do banco pelo ID."""
        # O import foi movido para o topo do arquivo (Clean Code)
        stmt = delete(Product).where(Product.id == product_id)
        self.session.execute(stmt)
        self.session.commit()