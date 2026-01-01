from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    
    # Dados da Empresa
    company_name: Mapped[str] = mapped_column(String, default="Minha Loja", init=False)
    cnpj: Mapped[str] = mapped_column(String, default="", init=False)
    address: Mapped[str] = mapped_column(String, default="", init=False)
    
    # Customização
    receipt_footer: Mapped[str] = mapped_column(String, default="Obrigado pela preferencia!", init=False)
    
    
    
    #Model: Tabela no Banco para guardar as configurações (Singleton - só terá 1 linha).