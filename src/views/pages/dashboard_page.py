import flet as ft
from decimal import Decimal

class DashboardPage(ft.Container):
    def __init__(self, page, product_service, sale_service):
        super().__init__()
        self.main_page = page
        self.product_service = product_service
        self.sale_service = sale_service
        
        self.expand = True
        self.padding = 30
        self.bgcolor = "#f3f4f6"

        # Elementos de Texto
        self.txt_vendas_hoje = ft.Text("R$ 0,00", color="white", size=24, weight="bold")
        self.txt_baixo_estoque = ft.Text("0", color="white", size=24, weight="bold")
        self.txt_ticket_medio = ft.Text("R$ 0,00", color="white", size=24, weight="bold")

        self.content = ft.Column([
            ft.Text("Visão Geral", size=28, weight="bold", color=ft.Colors.BLUE_GREY_900),
            ft.Text("Métricas em tempo real.", size=14, color=ft.Colors.GREY_600),
            ft.Divider(color="transparent", height=20),
            
            # Cards
            ft.Row([
                self._build_card("Vendas Hoje", self.txt_vendas_hoje, ft.Icons.ATTACH_MONEY, "green"),
                self._build_card("Alerta Estoque", self.txt_baixo_estoque, ft.Icons.WARNING_AMBER, "orange"),
                self._build_card("Ticket Médio", self.txt_ticket_medio, ft.Icons.TRENDING_UP, "blue"),
            ], spacing=20),
            
            ft.Divider(color="transparent", height=30),
            
            # Placeholder Gráfico
            ft.Container(
                content=ft.Column([
                    ft.Text("Status do Sistema", weight="bold", size=18, color=ft.Colors.BLUE_GREY_800),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=80, color=ft.Colors.GREEN_400),
                        alignment=ft.Alignment(0,0),
                        height=150
                    ),
                    ft.Text("Sistema Operacional e Conectado ao Banco de Dados.", color=ft.Colors.GREY_500, text_align="center")
                ]),
                bgcolor=ft.Colors.WHITE, padding=30, border_radius=15, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12), expand=True
            )
        ], expand=True)

    # --- MÁGICA DO CICLO DE VIDA ---
    # Este método é chamado AUTOMATICAMENTE pelo Flet quando a tela aparece.
    # Aqui é 100% seguro atualizar dados.
    def did_mount(self):
        self.atualizar_dados()

    def atualizar_dados(self):
        try:
            stats = self.sale_service.get_dashboard_stats()
            
            produtos = self.product_service.list_products()
            low_stock = sum(1 for p in produtos if p.stock_quantity < 10)
            
            self.txt_vendas_hoje.value = f"R$ {stats['vendas_hoje']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.txt_ticket_medio.value = f"R$ {stats['ticket_medio']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.txt_baixo_estoque.value = str(low_stock)
            
            self.update() # Agora é seguro chamar update()
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")

    def _build_card(self, titulo, controle_valor, icone, cor):
        cores = {
            "green": [ft.Colors.GREEN_600, ft.Colors.GREEN_400],
            "orange": [ft.Colors.ORANGE_600, ft.Colors.ORANGE_400],
            "blue": [ft.Colors.BLUE_600, ft.Colors.BLUE_400],
        }
        return ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                colors=cores.get(cor, [ft.Colors.GREY_600, ft.Colors.GREY_400])
            ),
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icone, color="white", size=30),
                    padding=10, bgcolor=ft.Colors.WHITE24, border_radius=10
                ),
                ft.Column([
                    ft.Text(titulo, color="white70", size=14),
                    controle_valor 
                ], spacing=0)
            ]),
            padding=20, border_radius=15, expand=True, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        )