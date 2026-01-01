#Esse serviço vai gerenciar o login e garantir que sempre exista pelo menos um usuário "admin" quando o sistema iniciar pela primeira vez.
import bcrypt
from sqlalchemy.orm import Session
from src.models.user import User

class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def _hash_password(self, password: str) -> str:
        # Gera o hash seguro da senha
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def _verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def initialize_admin(self):
        """Cria o usuário admin padrão se não existir"""
        admin = self.session.query(User).filter_by(username="admin").first()
        if not admin:
            hashed = self._hash_password("admin123") # Senha padrão
            new_admin = User(name="Administrador", username="admin", password_hash=hashed, role="admin")
            self.session.add(new_admin)
            self.session.commit()
            print("👤 Usuário 'admin' criado com senha 'admin123'")

    def login(self, username, password):
        user = self.session.query(User).filter_by(username=username, is_active=True).first()
        if user and self._verify_password(password, user.password_hash):
            return user
        return None
      
    # ... (métodos hash, verify e initialize_admin já existem) ...

    def create_user(self, name, username, password, role="operator"):
        """Cria um novo usuário no banco"""
        # Verifica se já existe
        existing = self.session.query(User).filter_by(username=username).first()
        if existing:
            raise ValueError("Nome de usuário já existe!")

        hashed = self._hash_password(password)
        new_user = User(name=name, username=username, password_hash=hashed, role=role)
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def list_users(self):
        """Lista todos os usuários"""
        return self.session.query(User).all()

    def delete_user(self, user_id):
        """Remove um usuário (exceto o admin principal)"""
        user = self.session.query(User).get(user_id)
        if user and user.username != "admin": # Proteção
            self.session.delete(user)
            self.session.commit()