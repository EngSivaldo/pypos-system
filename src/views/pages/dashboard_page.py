import flet as ft
from decimal import Decimal
import os
# --- IMPORTS NOVOS PARA O RELATÓRIO ---
from src.services.pdf_report import generate_sales_report
from src.database import SessionLocal 
# --------------------------------------

class DashboardPage(ft.Container):
    def __init__(self, page, product_service, sale_service):
        super().__init__()
        self.main_page = page
        self.product_service = product_service
        self.sale_service = sale_service
        
        self.expand = True
        self.padding = 30
        self.bgcolor = "#f3f4f6"

        # Elementos de Texto (Mantidos)
        self.txt_vendas_hoje = ft.Text("R$ 0,00", color="white", size=24, weight="bold")
        self.txt_baixo_estoque = ft.Text("0", color="white", size=24, weight="bold")
        self.txt_ticket_medio = ft.Text("R$ 0,00", color="white", size=24, weight="bold")

        # --- NOVO: Inicialização da Lista de Mais Vendidos ---
        self.lista_mais_vendidos = ft.Column(spacing=5)
        # -----------------------------------------------------

        # --- NOVO BOTÃO DE PDF ---
        self.btn_pdf = ft.ElevatedButton(
            "Baixar Relatório de Vendas (PDF)",
            icon=ft.Icons.PICTURE_AS_PDF,
            # Usei a forma "blindada" de alinhamento para evitar erros de versão
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_700,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=5
            ),
            on_click=self.gerar_pdf_click
        )
        # -------------------------

        self.content = ft.Column([
            ft.Text("Visão Geral", size=28, weight="bold", color=ft.Colors.BLUE_GREY_900),
            ft.Text("Métricas em tempo real.", size=14, color=ft.Colors.GREY_600),
            ft.Divider(color="transparent", height=20),
            
            # Cards de Indicadores
            ft.Row([
                self._build_card("Vendas Hoje", self.txt_vendas_hoje, ft.Icons.ATTACH_MONEY, "green"),
                self._build_card("Alerta Estoque", self.txt_baixo_estoque, ft.Icons.WARNING_AMBER, "orange"),
                self._build_card("Ticket Médio", self.txt_ticket_medio, ft.Icons.TRENDING_UP, "blue"),
            ], spacing=20),
            
            ft.Divider(color="transparent", height=20),

            # --- ÁREA DE AÇÕES E RANKING (Ajustado para incluir Mais Vendidos) ---
            ft.Row([
                # Coluna do Botão
                ft.Column([
                    ft.Text("Relatórios", size=18, weight="bold", color=ft.Colors.BLUE_GREY_800),
                    self.btn_pdf
                ], expand=1),
                
                # Coluna dos Mais Vendidos
                ft.Column([
                    ft.Text("Produtos Mais Vendidos", size=18, weight="bold", color=ft.Colors.BLUE_GREY_800),
                    ft.Container(
                        content=self.lista_mais_vendidos,
                        bgcolor=ft.Colors.WHITE,
                        padding=15,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.GREY_200)
                    )
                ], expand=1)
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
            # -----------------------------
            
            ft.Divider(color="transparent", height=20),
            
            # Placeholder Gráfico (Mantido)
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
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    # --- LÓGICA DO BOTÃO PDF ---
    def gerar_pdf_click(self, e):
        try:
            session = SessionLocal()
            caminho_arquivo = generate_sales_report(session)
            session.close()
            
            self.main_page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Relatório salvo em: {caminho_arquivo}"),
                bgcolor=ft.Colors.GREEN_700,
                duration=5000
            )
            self.main_page.snack_bar.open = True
            self.main_page.update()
            
            os.startfile(caminho_arquivo)
            
        except Exception as ex:
            print(f"Erro ao gerar PDF: {ex}")
            self.main_page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erro ao gerar relatório: {str(ex)}"),
                bgcolor=ft.Colors.RED_700
            )
            self.main_page.snack_bar.open = True
            self.main_page.update()

    # --- MÁGICA DO CICLO DE VIDA (MANTIDA) ---
    def did_mount(self):
        self.atualizar_dados()

    def atualizar_dados(self):
        try:
            stats = self.sale_service.get_dashboard_stats()
            
            # --- Atualiza a Lista de Mais Vendidos na UI ---
            self.lista_mais_vendidos.controls.clear()
            # Espera que stats['top_produtos'] seja uma lista de (nome, quantidade)
            top_produtos = stats.get('top_produtos', [])
            
            if not top_produtos:
                self.lista_mais_vendidos.controls.append(
                    ft.Text("Nenhuma venda registrada.", size=12, color=ft.Colors.GREY_500, italic=True)
                )
            else:
                for nome, qtd in top_produtos:
                    self.lista_mais_vendidos.controls.append(
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, color="amber", size=16),
                            ft.Text(f"{nome}", weight="bold", expand=True, size=14),
                            ft.Text(f"{qtd} un.", color="blue", weight="bold", size=14),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )

            # --- Atualiza os Cards Superiores ---
            produtos = self.product_service.list_products()
            # Verificação segura de atributo para estoque
            low_stock = sum(1 for p in produtos if getattr(p, 'stock_quantity', 0) < 10)
            
            self.txt_vendas_hoje.value = f"R$ {stats.get('vendas_hoje', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.txt_ticket_medio.value = f"R$ {stats.get('ticket_medio', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.txt_baixo_estoque.value = str(low_stock)
            
            self.update() 
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