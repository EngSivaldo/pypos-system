from sqlalchemy.orm import Session
from src.models.settings import AppSettings

class SettingsService:
    def __init__(self, session: Session):
        self.session = session

    def get_settings(self):
        """Busca a configuração. Se não existir, cria a padrão."""
        settings = self.session.query(AppSettings).first()
        if not settings:
            settings = AppSettings() # Cria vazio com os defaults do Model
            settings.company_name = "PYPOS ENTERPRISE"
            self.session.add(settings)
            self.session.commit()
            self.session.refresh(settings)
        return settings

    def save_settings(self, company_name, cnpj, address, footer):
        settings = self.get_settings() # Pega o existente
        
        settings.company_name = company_name
        settings.cnpj = cnpj
        settings.address = address
        settings.receipt_footer = footer
        
        self.session.commit()
        return settings
      
      
#A lógica aqui é: "Se não existir configuração, cria uma padrão. Se já existir, devolve ela."
