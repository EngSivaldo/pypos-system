import flet as ft

class PosPage(ft.Container):
    def __init__(self, page, product_service, sale_service):
        super().__init__()
        self.main_page = page
        self.product_service = product_service
        self.sale_service = sale_service
        self.expand = True
        self.padding = 20
        self.bgcolor = "#f3f4f6"

        self.carrinho = [] # Lista de itens da venda atual

        # --- Elementos da UI ---
        
        # Coluna Esquerda (Inputs)
        self.txt_codigo = ft.TextField(
            label="Código de Barras (Enter)", 
            autofocus=True, 
            prefix_icon=ft.Icons.QR_CODE_SCANNER,
            on_submit=self._adicionar_item,
            border_radius=10,
            text_size=16
        )
        self.txt_qtd = ft.TextField(
            label="Qtd", 
            value="1", 
            width=100, 
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            text_align=ft.TextAlign.CENTER
        )
        
        # Coluna Direita (Carrinho e Totais)
        self.txt_total = ft.Text("R$ 0,00", size=40, weight="bold", color=ft.Colors.BLUE_GREY_900)
        self.txt_itens_qtd = ft.Text("0 itens", size=16, color=ft.Colors.GREY_600)
        
        self.tabela_carrinho = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("PRODUTO", font_family="Roboto")),
                # CORREÇÃO AQUI: numeric=True pertence ao DataColumn, não ao Text
                ft.DataColumn(ft.Text("QTD"), numeric=True),
                ft.DataColumn(ft.Text("UNIT."), numeric=True),
                ft.DataColumn(ft.Text("TOTAL"), numeric=True),
            ],
            rows=[],
            border=ft.Border.all(1, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.WHITE,
            expand=True
        )

        # --- Montagem do Layout ---
        
        # Painel Esquerdo: Busca
        painel_busca = ft.Container(
            content=ft.Column([
                ft.Text("Registrar Item", size=20, weight="bold", color=ft.Colors.BLUE_GREY_800),
                ft.Divider(),
                ft.Row([self.txt_codigo, self.txt_qtd]),
                ft.ElevatedButton(
                    "Adicionar Item", 
                    icon=ft.Icons.ADD_SHOPPING_CART, 
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_600, 
                        color=ft.Colors.WHITE, 
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    width=300,
                    on_click=self._adicionar_item
                ),
                ft.Divider(height=50, color="transparent"),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TIPS_AND_UPDATES, color=ft.Colors.ORANGE_400),
                        ft.Text("Dica: Use um leitor de código de barras ou digite o código e pressione Enter.", 
                                color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.Alignment(0,0)
                )
            ]),
            bgcolor=ft.Colors.WHITE,
            padding=30,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK12),
            expand=1
        )

        # Painel Direito: Cupom
        painel_cupom = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Carrinho de Compras", size=20, weight="bold", color=ft.Colors.BLUE_GREY_800),
                    self.txt_itens_qtd
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Container(self.tabela_carrinho, expand=True, border=ft.border.all(1, "#e5e7eb"), border_radius=8),
                ft.Divider(),
                ft.Row([
                    ft.Text("Total a Pagar:", size=18, weight="bold", color=ft.Colors.GREY_700),
                    self.txt_total
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "FINALIZAR VENDA", 
                    icon=ft.Icons.CHECK_CIRCLE,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_600, 
                        color=ft.Colors.WHITE, 
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    ),
                    on_click=self._finalizar_venda,
                    expand=True
                )
            ]),
            bgcolor=ft.Colors.WHITE,
            padding=30,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK12),
            expand=2
        )

        self.content = ft.Row([painel_busca, painel_cupom], spacing=20, expand=True)

    def _adicionar_item(self, e):
        codigo = self.txt_codigo.value
        if not codigo: return

        try:
            qtd = int(self.txt_qtd.value)
            if qtd <= 0: raise ValueError
        except:
            self._notificar("Quantidade inválida!", False)
            return

        # Busca produto (Simulação - idealmente o service teria get_by_barcode)
        todos = self.product_service.list_products()
        produto = next((p for p in todos if p.barcode == codigo), None)

        if not produto:
            self._notificar(f"Produto '{codigo}' não encontrado.", False)
            return
        
        if produto.stock_quantity < qtd:
            self._notificar(f"Estoque insuficiente! Restam {produto.stock_quantity}.", False)
            return

        # Adiciona ao carrinho
        self.carrinho.append({'prod': produto, 'qtd': qtd})
        self._atualizar_ui_carrinho()
        
        self.txt_codigo.value = ""
        self.txt_codigo.focus()
        self.update()

    def _atualizar_ui_carrinho(self):
        self.tabela_carrinho.rows.clear()
        total = 0.0
        itens = 0

        for item in self.carrinho:
            p = item['prod']
            q = item['qtd']
            subtotal = p.price * q
            total += subtotal
            itens += q

            self.tabela_carrinho.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p.name)),
                    ft.DataCell(ft.Text(str(q))),
                    ft.DataCell(ft.Text(f"R$ {p.price:.2f}")),
                    ft.DataCell(ft.Text(f"R$ {subtotal:.2f}", weight="bold")),
                ])
            )

        self.txt_total.value = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.txt_itens_qtd.value = f"{itens} itens"
        self.update()

    def _finalizar_venda(self, e):
        if not self.carrinho:
            self._notificar("Carrinho vazio!", False)
            return

        try:
            payload = [{'barcode': i['prod'].barcode, 'quantity': i['qtd']} for i in self.carrinho]
            self.sale_service.create_sale(payload)
            
            self._notificar("Venda realizada com sucesso!", True)
            self.carrinho = []
            self._atualizar_ui_carrinho()
            
        except Exception as ex:
            self._notificar(f"Erro: {ex}", False)

    def _notificar(self, msg, sucesso):
        self.main_page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="green" if sucesso else "red")
        self.main_page.snack_bar.open = True
        self.main_page.update()