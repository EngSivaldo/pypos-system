# Arquivo: src/main.py
import sys
import os
# --- 🔧 CORREÇÃO DE IMPORTS (O Truque Sênior) ---
# Isso faz o Python enxergar a pasta raiz 'pypos_system'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ------------------------------------------------


import flet as ft
from sqlalchemy import create_engine, event 
from sqlalchemy.orm import Session
from src.config.settings import DATABASE_URL

# ✅ 1. IMPORTANDO AS FERRAMENTAS DE SEGURANÇA (Do arquivo utils.py vizinho)
# Certifique-se de que utils.py está na mesma pasta src/
from utils import configurar_logs, realizar_backup_banco

# Importação dos Serviços
from src.services.product_service import ProductService
from src.services.sale_service import SaleService
from src.services.settings_service import SettingsService
from src.services.auth_service import AuthService

# Importação das Páginas (Views)
from src.views.pages.inventory_page import InventoryPage
from src.views.pages.pos_page import PosPage
from src.views.pages.dashboard_page import DashboardPage
from src.views.pages.history_page import HistoryPage
from src.views.pages.settings_page import SettingsPage
from src.views.login_view import LoginView
from src.views.pages.users_page import UsersPage

def main(page: ft.Page):
    # --- 🛡️ ROTINAS DE SEGURANÇA (PRIMEIRA COISA A RODAR) ---
    print("🛡️ Iniciando protocolos de segurança...")
    configurar_logs()       # Liga o gravador de erros
    realizar_backup_banco() # Faz o backup antes de tudo
    # --------------------------------------------------------

    # Configuração da Janela
    page.title = "PyPOS | Enterprise"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_min_width = 1200
    page.window_min_height = 800
    page.padding = 0
    page.bgcolor = "#f3f4f6"
    page.fonts = {"Roboto": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"}
    page.theme = ft.Theme(font_family="Roboto")

    # --- Backend e Banco de Dados ---
    try:
        engine = create_engine(DATABASE_URL)

        # --- 🛡️ BLINDAGEM DO BANCO (WAL MODE) ---
        # Protege contra quedas de energia e melhora performance
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
        # ----------------------------------------
        
        from src.models.base import Base
        # Import models para garantir criação das tabelas
        from src.models.product import Product 
        from src.models.sale import Sale
        from src.models.settings import AppSettings
        from src.models.user import User
        
        # Cria as tabelas se não existirem
        Base.metadata.create_all(engine) 

        session = Session(engine)
        
        # Instancia Serviços
        product_service = ProductService(session)
        sale_service = SaleService(session)
        settings_service = SettingsService(session)
        auth_service = AuthService(session)
        
        # Garante que existe o usuário admin padrão
        auth_service.initialize_admin()
        
        print("✅ Backend inicializado e pronto (Modo Seguro Ativado).")
        
    except Exception as e:
        print(f"❌ Erro Crítico de Banco: {e}")
        # Aqui poderíamos fechar o app ou mostrar alerta
        return

    # --- Lógica de Navegação e UI ---
    current_user = None

    # Função Principal do App (Pós-Login)
    def iniciar_app_principal(user):
        nonlocal current_user
        current_user = user
        
        page.clean()
        page.bgcolor = "#f3f4f6"

        # Instancia Páginas
        inventory_page = InventoryPage(page, product_service)
        pos_page = PosPage(page, product_service, sale_service, settings_service)
        dashboard_page = DashboardPage(page, product_service, sale_service)
        history_page = HistoryPage(page, sale_service)
        settings_page = SettingsPage(page, settings_service)
        users_page = UsersPage(page, auth_service) 

        content_area = ft.Container(content=inventory_page, expand=True)

        def navegar(e):
            page_id = e.control.data
            # Lógica de troca de abas
            if page_id == "estoque":
                content_area.content = inventory_page
                inventory_page.carregar_dados()
            elif page_id == "caixa":
                content_area.content = pos_page
            elif page_id == "dashboard":
                content_area.content = dashboard_page
            elif page_id == "historico":
                content_area.content = history_page
            elif page_id == "config":
                content_area.content = settings_page
            elif page_id == "usuarios":
                content_area.content = users_page
                        
            content_area.update()

        def logout(e):
            page.clean()
            carregar_login()

        def menu_button(text, icon, data_id, is_logout=False):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(icon, color=ft.Colors.WHITE70, size=20),
                    ft.Text(text, color=ft.Colors.WHITE, size=14, weight="w500")
                ], spacing=15),
                padding=15, border_radius=8, ink=True,
                on_click=navegar if not is_logout else logout,
                data=data_id
            )

        # Informações do Usuário na Sidebar
        user_info = ft.Container(
            content=ft.Row([
                ft.CircleAvatar(content=ft.Text(user.username[0].upper()), bgcolor=ft.Colors.BLUE_600),
                ft.Column([
                    ft.Text(user.name, color="white", weight="bold"),
                    ft.Text(user.role.upper(), color="grey", size=10)
                ], spacing=0)
            ]),
            padding=10, bgcolor=ft.Colors.WHITE10, border_radius=10
        )

        # Sidebar
        sidebar_items = [
            ft.Row([
                ft.Icon(ft.Icons.ROCKET_LAUNCH, color=ft.Colors.BLUE_400, size=28),
                ft.Text("PyPOS", color=ft.Colors.WHITE, size=22, weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color=ft.Colors.WHITE10, height=20),
            user_info,
            ft.Divider(color=ft.Colors.WHITE10, height=20),
            ft.Text("MENU", color=ft.Colors.GREY_500, size=11, weight="bold"),
            ft.Container(height=5),
        ]

        # Itens Comuns
        sidebar_items.append(menu_button("Vendas (PDV)", ft.Icons.POINT_OF_SALE, "caixa"))
        sidebar_items.append(menu_button("Estoque", ft.Icons.INVENTORY_2_OUTLINED, "estoque"))

        # Itens de Admin
        if user.role == "admin":
            sidebar_items.append(menu_button("Dashboard", ft.Icons.DASHBOARD_OUTLINED, "dashboard"))
            sidebar_items.append(menu_button("Histórico", ft.Icons.HISTORY, "historico"))
            sidebar_items.append(menu_button("Equipe", ft.Icons.PEOPLE, "usuarios"))
            ft.Divider(color=ft.Colors.WHITE10),
            sidebar_items.append(menu_button("Configurações", ft.Icons.SETTINGS, "config"))

        # Rodapé
        sidebar_items.append(ft.Container(expand=True))
        sidebar_items.append(menu_button("Sair", ft.Icons.LOGOUT, "logout", is_logout=True))

        sidebar = ft.Container(
            width=260, bgcolor="#111827", padding=20,
            content=ft.Column(sidebar_items)
        )

        layout = ft.Row([sidebar, content_area], expand=True, spacing=0)
        page.add(layout)
        inventory_page.carregar_dados()

    # Função de Login Inicial
    def carregar_login():
        page.bgcolor = "#111827" 
        login_view = LoginView(page, auth_service, on_login_success=iniciar_app_principal)
        page.add(login_view)

    # O APP COMEÇA AQUI
    carregar_login()

if __name__ == "__main__":
    ft.app(target=main)