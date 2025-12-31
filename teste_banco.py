from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.config.settings import DATABASE_URL
from src.models.product import Product
from src.repositories.product_repository import ProductRepository

# 1. Configura conexão
engine = create_engine(DATABASE_URL)

# 2. Abre uma sessão (transação)
with Session(engine) as session:
    repo = ProductRepository(session)
    
    # 3. Cria um produto falso
    print("💾 Tentando salvar Coca-Cola...")
    try:
        novo_prod = Product(
            barcode="7894900011517",
            name="Coca-Cola 2L",
            price=Decimal("10.50"),
            stock_quantity=100
        )
        repo.add(novo_prod)
        print(f"✅ Sucesso! Produto criado com ID: {novo_prod.id}")
    except Exception as e:
        print(f"⚠️ Erro (talvez já exista): {e}")

    # 4. Busca para conferir
    prod = repo.get_by_barcode("7894900011517")
    if prod:
        print(f"🔍 Busca Confirmada: {prod.name} custa R$ {prod.price}")