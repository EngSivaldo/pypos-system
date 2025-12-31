# Base do SQLAlchemy (Declarative Base)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

class Base(DeclarativeBase, MappedAsDataclass):
    """
    Classe base para todos os modelos do SQLAlchemy 2.0.
    MappedAsDataclass: Permite criar objetos sem definir __init__ manualmente.
    """
    pass