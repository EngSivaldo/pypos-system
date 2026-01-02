from sqlalchemy import create_engine, event  # <--- 1. ADICIONAR 'event' AQUI
from src.config.settings import DATABASE_URL
from src.models.base import Base

# Importar modelos para registrar
from src.models.product import Product
from src.models.sale import Sale

# --- FUNÇÃO DE PROTEÇÃO (WAL MODE) ---
def configurar_banco_seguro(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # Ativa modo contra falhas
    cursor.execute("PRAGMA synchronous=NORMAL") # Aumenta velocidade
    cursor.close()
# -------------------------------------

def init_database():
    """
    Função utilitária para criar as tabelas no banco de dados.
    """
    print(f"🔌 Conectando ao banco em: {DATABASE_URL}")
    
    # Cria a engine
    engine = create_engine(DATABASE_URL)
    
    # --- LIGAR A PROTEÇÃO NA ENGINE ---
    event.listen(engine, 'connect', configurar_banco_seguro)
    # ----------------------------------
    
    print("🏗️  Criando tabelas...")
    Base.metadata.create_all(engine)
    
    print("✅ Banco de dados inicializado com blindagem WAL!")

if __name__ == "__main__":
    init_database()