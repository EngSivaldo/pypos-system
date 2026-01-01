from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base

class User(Base):
    __tablename__ = "users"

    # A CORREÇÃO ESTÁ AQUI (init=False):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    
    # Para evitar erros futuros, vamos definir valores padrão no Python também
    role: Mapped[str] = mapped_column(String(20), default="operator") 
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)