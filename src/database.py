from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.settings import DATABASE_URL

# Cria a conexão com o banco de dados
engine = create_engine(DATABASE_URL)

# Cria a fábrica de sessões (usada para criar sessões temporárias, como no relatório PDF)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)