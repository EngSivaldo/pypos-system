from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.repositories.product_repository import ProductRepository
from src.models.product import Product

class ProductService:
    def __init__(self, session: Session):
        self.repository = ProductRepository(session)

    def create_product(self, name: str, barcode: str, price: str | float, stock: int, category: str = "Geral") -> Product:
        """Cria um produto incluindo agora a CATEGORIA."""
        # 1. Validações
        if not name or len(name.strip()) < 3:
            raise ValueError("O nome do produto deve ter pelo menos 3 letras.")
        if not barcode:
            raise ValueError("O código de barras é obrigatório.")

        # 2. Tratamento Monetário
        try:
            price_decimal = Decimal(str(price))
            if price_decimal <= 0:
                raise ValueError("O preço deve ser maior que zero.")
        except Exception:
            raise ValueError("Preço inválido.")

        # 3. Criação do Objeto (ADICIONADO CATEGORY AQUI)
        product = Product(
            name=name,
            barcode=barcode,
            price=price_decimal,
            stock_quantity=stock,
            category=category  # <--- ESSENCIAL
        )

        # 4. Persistência
        try:
            saved_product = self.repository.add(product)
            return saved_product
        except IntegrityError:
            self.repository.session.rollback()
            raise ValueError(f"Já existe um produto com o código de barras {barcode}.")

    def update_product(self, product_id: int, name: str, price: str | float, stock: int, category: str = "Geral"):
        """Atualiza o produto incluindo a CATEGORIA."""
        if not name or len(name.strip()) < 3:
            raise ValueError("O nome do produto deve ter pelo menos 3 letras.")
        
        try:
            price_decimal = Decimal(str(price))
            if price_decimal <= 0:
                raise ValueError("O preço deve ser maior que zero.")
        except Exception:
            raise ValueError("Preço inválido.")

        # Chama o repositório passando a categoria também
        # IMPORTANTE: Garanta que seu ProductRepository.update aceite o argumento category!
        self.repository.update(product_id, name, price_decimal, stock, category)

    def list_products(self):
        return self.repository.get_all()

    def delete_product(self, product_id: int):
        try:
            self.repository.delete(product_id)
        except Exception as e:
            self.repository.session.rollback()
            if "foreign key" in str(e).lower():
                raise ValueError("Não é possível deletar este produto pois ele já possui vendas registradas.")
            raise e