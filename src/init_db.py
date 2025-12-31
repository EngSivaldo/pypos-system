from sqlalchemy import create_engine
from src.config.settings import DATABASE_URL
from src.models.base import Base

# --- IMPORTANTE ---
# Precisamos importar os modelos aqui, mesmo que não os usemos diretamente.
# Ao importar, o SQLAlchemy "registra" as classes no sistema.
from src.models.product import Product
from src.models.sale import Sale
# ------------------

def init_database():
    """
    Função utilitária para criar as tabelas no banco de dados.
    Em produção, usaríamos o Alembic (ferramenta de migração), 
    mas para este MVP, o create_all resolve.
    """
    print(f"🔌 Conectando ao banco em: {DATABASE_URL}")
    
    # Cria a engine (o motor de conexão)
    engine = create_engine(DATABASE_URL)
    
    print("🏗️  Criando tabelas...")
    # Este comando olha para todos os modelos que herdam de 'Base' e cria as tabelas
    Base.metadata.create_all(engine)
    
    print("✅ Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_database()