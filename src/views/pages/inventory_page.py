import flet as ft
from src.views.components.product_modal import ProductModal

class InventoryPage(ft.Container):
    def __init__(self, page, product_service):
        super().__init__()
        self.main_page = page 
        self.service = product_service
        self.expand = True
        self.padding = 20
        self.bgcolor = "#f3f4f6"
        
        self.modal = ProductModal(self.main_page, self._salvar_backend)

        # --- Componentes de UI ---
        
        # KPIs (Indicadores)
        self.card_total = self._criar_kpi_card("Total Itens", "0", ft.Icons.INVENTORY_2, ft.Colors.BLUE_600, ft.Colors.BLUE_400)
        self.card_valor = self._criar_kpi_card("Valor em Estoque", "R$ 0,00", ft.Icons.ATTACH_MONEY, ft.Colors.ORANGE_600, ft.Colors.ORANGE_400)

        # Tabela Estilizada
        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("CÓDIGO", weight="bold", color=ft.Colors.GREY_700)),
                ft.DataColumn(ft.Text("PRODUTO", weight="bold", color=ft.Colors.GREY_700)),
                ft.DataColumn(ft.Text("PREÇO", weight="bold", color=ft.Colors.GREY_700), numeric=True),
                ft.DataColumn(ft.Text("ESTOQUE", weight="bold", color=ft.Colors.GREY_700), numeric=True),
                ft.DataColumn(ft.Text("AÇÕES", weight="bold", color=ft.Colors.GREY_700)),
            ],
            rows=[], 
            border=ft.Border.all(1, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.WHITE,
            heading_row_height=60,
            data_row_min_height=50,
            expand=True,
            column_spacing=20
        )

        # Container da Tabela
        self.container_tabela = ft.Container(
            content=ft.Column([self.tabela], scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=10,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        )

        # Header
        header = ft.Row([
            ft.Column([
                ft.Text("Controle de Estoque", size=24, weight="bold", color=ft.Colors.BLUE_GREY_900),
                ft.Text("Gerencie entradas, saídas e catálogo.", size=14, color=ft.Colors.GREY_500),
            ]),
            ft.ElevatedButton(
                "Novo Produto", 
                icon=ft.Icons.ADD, 
                on_click=lambda e: self.modal.abrir(),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_700, 
                    color=ft.Colors.WHITE,
                    padding=20,
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Montagem Final
        self.content = ft.Column([
            header,
            ft.Container(height=10),
            ft.Row([self.card_total, self.card_valor], spacing=20),
            ft.Container(height=10),
            self.container_tabela
        ], expand=True)
        
        self.carregar_dados(inicial=True)

    def _criar_kpi_card(self, titulo, valor, icone, cor1, cor2):
        return ft.Container(
            gradient=ft.LinearGradient(
                # CORREÇÃO SÊNIOR: Uso de coordenadas numéricas para evitar erros de versão
                begin=ft.Alignment(-1, -1), # Top Left
                end=ft.Alignment(1, 1),     # Bottom Right
                colors=[cor1, cor2],
            ),
            content=ft.Row([
                ft.Container(
                    padding=10, 
                    bgcolor=ft.Colors.WHITE24, 
                    border_radius=10,
                    content=ft.Icon(icone, color=ft.Colors.WHITE, size=24)
                ),
                ft.Column([
                    ft.Text(titulo, color=ft.Colors.WHITE70, size=12, weight="w500"),
                    ft.Text(valor, color=ft.Colors.WHITE, size=20, weight="bold")
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            border_radius=15,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        )

    def carregar_dados(self, inicial=False):
        self.tabela.rows.clear()
        try:
            produtos = self.service.list_products()
            
            # Atualiza os Cards
            total_items = len(produtos)
            total_value = sum(p.price * p.stock_quantity for p in produtos)
            
            self.card_total.content.controls[1].controls[1].value = str(total_items)
            self.card_valor.content.controls[1].controls[1].value = f"R$ {total_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            for p in produtos:
                btn_edit = ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=ft.Colors.BLUE_600, tooltip="Editar", data=p, on_click=lambda e: self.modal.abrir(e.control.data))
                btn_del = ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, tooltip="Excluir", data=p.id, on_click=self._deletar)
                
                # Tag de Estoque
                status_color = ft.Colors.GREEN_100 if p.stock_quantity > 10 else ft.Colors.RED_100
                status_text = ft.Colors.GREEN_800 if p.stock_quantity > 10 else ft.Colors.RED_800
                
                tag_estoque = ft.Container(
                    content=ft.Text(str(p.stock_quantity), size=12, weight="bold", color=status_text),
                    bgcolor=status_color,
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=20,
                    # CORREÇÃO SÊNIOR: Uso de coordenadas numéricas para Center
                    alignment=ft.Alignment(0, 0)
                )

                self.tabela.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(p.barcode, size=12)),
                        ft.DataCell(ft.Text(p.name, weight="bold")),
                        ft.DataCell(ft.Text(f"R$ {p.price:.2f}")),
                        ft.DataCell(tag_estoque),
                        ft.DataCell(ft.Row([btn_edit, btn_del], spacing=0)),
                    ])
                )
            
            if not inicial and self.page: self.update()
                
        except Exception as e:
            print(f"Erro ao carregar: {e}")

    def _salvar_backend(self, dados):
        try:
            if dados['id']:
                self.service.update_product(dados['id'], dados['name'], dados['price'], int(dados['stock']))
                msg = "Produto Atualizado!"
            else:
                self.service.create_product(dados['name'], dados['barcode'], dados['price'], int(dados['stock']))
                msg = "Produto Criado!"
            self.main_page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="green")
            self.main_page.snack_bar.open = True
            self.main_page.update()
            self.carregar_dados() 
        except Exception as e:
            self.main_page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {e}"), bgcolor="red")
            self.main_page.snack_bar.open = True
            self.main_page.update()

    def _deletar(self, e):
        try:
            self.service.delete_product(e.control.data)
            self.carregar_dados()
            self.main_page.snack_bar = ft.SnackBar(ft.Text("Deletado!"), bgcolor="green")
            self.main_page.snack_bar.open = True
            self.main_page.update()
        except Exception as ex:
            self.main_page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor="red")
            self.main_page.snack_bar.open = True
            self.main_page.update()