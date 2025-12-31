import flet as ft
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.config.settings import DATABASE_URL
from src.services.product_service import ProductService
from src.services.sale_service import SaleService

# Importação das Páginas Modulares
from src.views.pages.inventory_page import InventoryPage
from src.views.pages.pos_page import PosPage
from src.views.pages.dashboard_page import DashboardPage

def main(page: ft.Page):
    # --- Configuração da Janela ---
    page.title = "PyPOS | Enterprise"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_min_width = 1200
    page.window_min_height = 800
    page.padding = 0
    page.bgcolor = "#f3f4f6"
    
    # Fonte padrão bonita
    page.fonts = {"Roboto": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"}
    page.theme = ft.Theme(font_family="Roboto")

    # --- Backend ---
    try:
        engine = create_engine(DATABASE_URL)
        session = Session(engine)
        product_service = ProductService(session)
        sale_service = SaleService(session)
    except Exception as e:
        print(f"Erro Crítico de Banco: {e}")
        return

    # --- Instancia as Páginas ---
    inventory_page = InventoryPage(page, product_service)
    pos_page = PosPage(page, product_service, sale_service)
    dashboard_page = DashboardPage(page)

    # Área de Conteúdo (Dinâmica)
    content_area = ft.Container(content=inventory_page, expand=True)

    def navegar(e):
        page_id = e.control.data
        
        if page_id == "estoque":
            content_area.content = inventory_page
            inventory_page.carregar_dados() # Atualiza tabela ao entrar
        elif page_id == "caixa":
            content_area.content = pos_page
            # Opcional: focar no input ao entrar
            pos_page.txt_codigo.focus()
        elif page_id == "dashboard":
            content_area.content = dashboard_page
            # Futuro: dashboard_page.atualizar_dados()
            
        content_area.update()

    def menu_button(text, icon, data_id, is_logout=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ft.Colors.WHITE70, size=20),
                ft.Text(text, color=ft.Colors.WHITE, size=14, weight="w500")
            ], spacing=15),
            padding=ft.padding.symmetric(vertical=12, horizontal=15),
            border_radius=8,
            ink=True,
            on_click=navegar if not is_logout else lambda _: page.window_close(),
            data=data_id
        )

    # --- Sidebar ---
    sidebar = ft.Container(
        width=260,
        bgcolor="#111827",
        padding=20,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ROCKET_LAUNCH, color=ft.Colors.BLUE_400, size=28),
                ft.Text("PyPOS", color=ft.Colors.WHITE, size=22, weight="bold")
            ], alignment="center"),
            
            ft.Divider(color=ft.Colors.WHITE10, height=30),
            
            ft.Text("MENU", color=ft.Colors.GREY_500, size=11, weight="bold"),
            ft.Container(height=5),
            menu_button("Dashboard", ft.Icons.DASHBOARD_OUTLINED, "dashboard"),
            menu_button("Estoque", ft.Icons.INVENTORY_2_OUTLINED, "estoque"),
            menu_button("Vendas (PDV)", ft.Icons.POINT_OF_SALE, "caixa"),
            
            ft.Container(expand=True),
            
            ft.Divider(color=ft.Colors.WHITE10),
            menu_button("Sair", ft.Icons.LOGOUT, "logout", is_logout=True)
        ])
    )

    layout = ft.Row([sidebar, content_area], expand=True, spacing=0)
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)