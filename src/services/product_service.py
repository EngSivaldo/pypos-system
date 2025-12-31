#product_service.py (Gerente de Estoque): Cuida de tudo relacionado ao produto (Criar, Editar preço, Listar). Foi o que fizemos agora.

from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.repositories.product_repository import ProductRepository
from src.models.product import Product

class ProductService:
    """
    Camada de Regra de Negócio.
    Aqui validamos se os dados fazem sentido antes de chamar o banco.
    """

    def __init__(self, session: Session):
        self.repository = ProductRepository(session)

    def create_product(self, name: str, barcode: str, price: str | float, stock: int) -> Product:
        """
        Cria um produto validando regras de negócio.
        Recebe 'price' como string ou float, mas converte para Decimal internamente.
        """
        # 1. Validações de Negócio (Fail Fast)
        if not name or len(name.strip()) < 3:
            raise ValueError("O nome do produto deve ter pelo menos 3 letras.")
        
        if not barcode:
            raise ValueError("O código de barras é obrigatório.")

        # 2. Tratamento Monetário Seguro
        try:
            # Convertemos para string antes de Decimal para evitar imprecisão de float
            price_decimal = Decimal(str(price))
            if price_decimal <= 0:
                raise ValueError("O preço deve ser maior que zero.")
        except Exception:
            raise ValueError("Preço inválido.")

        # 3. Criação do Objeto
        product = Product(
            name=name,
            barcode=barcode,
            price=price_decimal,
            stock_quantity=stock
        )

        # 4. Tentativa de Persistência com Tratamento de Erro
        try:
            saved_product = self.repository.add(product)
            return saved_product
        except IntegrityError:
            # Se o banco reclamar de chave duplicada (barcode igual), traduzimos o erro
            # O 'rollback' é vital aqui, senão a sessão trava.
            self.repository.session.rollback()
            raise ValueError(f"Já existe um produto com o código de barras {barcode}.")

    def list_products(self):
        return self.repository.get_all()