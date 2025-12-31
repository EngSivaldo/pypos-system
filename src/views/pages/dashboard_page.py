import flet as ft

class DashboardPage(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.expand = True
        self.padding = 30
        self.bgcolor = "#f3f4f6"

        self.content = ft.Column([
            ft.Text("Visão Geral", size=28, weight="bold", color=ft.Colors.BLUE_GREY_900),
            ft.Text("Acompanhe o desempenho da sua loja.", size=14, color=ft.Colors.GREY_600),
            ft.Divider(color="transparent", height=20),
            
            # Linha de Cards
            ft.Row([
                self._build_card("Vendas Hoje", "R$ 0,00", ft.Icons.ATTACH_MONEY, "green"),
                self._build_card("Produtos Baixo Estoque", "0", ft.Icons.WARNING_AMBER, "orange"),
                self._build_card("Ticket Médio", "R$ 0,00", ft.Icons.TRENDING_UP, "blue"),
            ], spacing=20),
            
            ft.Divider(color="transparent", height=30),
            
            # Área de Gráfico (Simulada Visualmente)
            ft.Container(
                content=ft.Column([
                    ft.Text("Histórico de Vendas (Últimos 7 dias)", weight="bold", size=18, color=ft.Colors.BLUE_GREY_800),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Icon(ft.Icons.INSERT_CHART_OUTLINED, size=100, color=ft.Colors.GREY_300),
                        alignment=ft.Alignment(0,0),
                        height=200
                    ),
                    ft.Text("Gráficos serão exibidos aqui após as primeiras vendas.", color=ft.Colors.GREY_400, text_align="center")
                ]),
                bgcolor=ft.Colors.WHITE,
                padding=30,
                border_radius=15,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                expand=True
            )
        ], expand=True)

    def _build_card(self, titulo, valor, icone, cor):
        # Mapeamento de cores
        cores = {
            "green": [ft.Colors.GREEN_600, ft.Colors.GREEN_400],
            "orange": [ft.Colors.ORANGE_600, ft.Colors.ORANGE_400],
            "blue": [ft.Colors.BLUE_600, ft.Colors.BLUE_400],
        }
        bg_gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
            colors=cores.get(cor, [ft.Colors.GREY_600, ft.Colors.GREY_400])
        )
        
        return ft.Container(
            gradient=bg_gradient,
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icone, color="white", size=30),
                    padding=10, bgcolor=ft.Colors.WHITE24, border_radius=10
                ),
                ft.Column([
                    ft.Text(titulo, color="white70", size=14),
                    ft.Text(valor, color="white", size=24, weight="bold")
                ], spacing=0)
            ]),
            padding=20,
            border_radius=15,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        )