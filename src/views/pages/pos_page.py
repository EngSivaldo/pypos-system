import flet as ft
from decimal import Decimal
import os
from datetime import datetime
import subprocess

class PosPage(ft.Container):
    def __init__(self, page, product_service, sale_service, settings_service):
        super().__init__()
        self.main_page = page
        self.product_service = product_service
        self.sale_service = sale_service
        self.settings_service = settings_service
        self.expand = True
        self.padding = 20
        self.bgcolor = "#f3f4f6"

        self.carrinho = [] 
        self.item_para_editar_index = None 
        self.item_para_remover_index = None # Variável de controle para remoção

        try:
            self.lista_produtos = self.product_service.list_products()
        except Exception:
            self.lista_produtos = []

        # --- MODAL CONFIRMAR REMOÇÃO (NOVO) ---
        self.dialog_delete = ft.AlertDialog(
            modal=True,
            title=ft.Text("Remover do Carrinho"),
            content=ft.Text("Tem certeza que deseja remover este item?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_modal_delete),
                ft.ElevatedButton("Sim, Remover", bgcolor="red", color="white", on_click=self._confirmar_remover_item)
            ]
        )
        self.main_page.overlay.append(self.dialog_delete)

        # --- MODAL EDITAR QTD ---
        self.txt_edit_qtd = ft.TextField(label="Nova Qtd", autofocus=True, keyboard_type=ft.KeyboardType.NUMBER)
        self.dialog_edit = ft.AlertDialog(
            modal=True, 
            title=ft.Text("Editar Item"), 
            content=self.txt_edit_qtd,
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_modal_edit),
                ft.FilledButton("Salvar", on_click=self._salvar_edicao_item)
            ]
        )
        self.main_page.overlay.append(self.dialog_edit)

        # --- MODAL CHECKOUT ---
        self.txt_checkout_total = ft.Text("R$ 0,00", size=40, weight="bold", color=ft.Colors.GREEN_700, text_align="center")
        self.txt_checkout_itens = ft.Text("0 itens", color="grey")
        self.switch_imprimir = ft.Switch(label="Imprimir Comprovante", value=True, active_color=ft.Colors.BLUE_600)

        opcoes_pagamento = ft.Row([
            self._btn_pagamento(ft.Icons.MONEY, "Dinheiro", True),
            self._btn_pagamento(ft.Icons.CREDIT_CARD, "Crédito", False),
            self._btn_pagamento(ft.Icons.CREDIT_CARD, "Débito", False),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        self.dialog_checkout = ft.AlertDialog(
            modal=True,
            title=ft.Text("Finalizar Venda", weight="bold", text_align="center"),
            content=ft.Column([
                ft.Container(height=10),
                ft.Text("Total a Pagar:", size=14, color=ft.Colors.GREY_600, text_align="center"),
                ft.Container(self.txt_checkout_total, alignment=ft.Alignment(0, 0)),
                ft.Container(self.txt_checkout_itens, alignment=ft.Alignment(0, 0)),
                ft.Divider(height=20),
                ft.Text("Opções:", size=12, weight="bold"),
                ft.Container(self.switch_imprimir, alignment=ft.Alignment(0,0)),
                ft.Divider(height=10),
                ft.Text("Forma de Pagamento:", size=12, weight="bold"),
                opcoes_pagamento,
            ], tight=True, width=400),
            actions=[
                ft.OutlinedButton("Cancelar", on_click=self._fechar_modal_checkout, style=ft.ButtonStyle(color=ft.Colors.RED_400)),
                ft.FilledButton("CONFIRMAR PAGAMENTO", icon=ft.Icons.CHECK, on_click=self._efetivar_venda_backend, 
                                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, padding=15))
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        self.main_page.overlay.append(self.dialog_checkout)

        # --- UI ELEMENTS ---
        self.info_preview_nome = ft.Text("-", size=16, weight="bold", color=ft.Colors.BLUE_GREY_900)
        self.info_preview_preco = ft.Text("R$ 0,00", size=16, weight="bold", color=ft.Colors.GREEN_700)
        
        self.card_preview = ft.Container(
            visible=False, bgcolor=ft.Colors.BLUE_50, padding=15, border_radius=10,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            content=ft.Column([
                ft.Text("Produto Identificado:", size=10, weight="bold"),
                self.info_preview_nome, self.info_preview_preco
            ], spacing=2)
        )

        self.txt_codigo = ft.TextField(
            label="Código de Barras", autofocus=True, prefix_icon=ft.Icons.QR_CODE_SCANNER,
            on_submit=self._adicionar_item, on_change=self._buscar_preview, border_radius=10, text_size=16
        )
        
        self.txt_qtd = ft.TextField(
            label="Qtd", value="1", width=100, keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10, text_align=ft.TextAlign.CENTER
        )
        
        self.txt_total = ft.Text("R$ 0,00", size=40, weight="bold", color=ft.Colors.BLUE_GREY_900)
        self.txt_itens_qtd = ft.Text("0 itens", size=16, color=ft.Colors.GREY_600)
        
        self.tabela_carrinho = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("PRODUTO")),
                ft.DataColumn(ft.Text("QTD"), numeric=True),
                ft.DataColumn(ft.Text("UNIT."), numeric=True),
                ft.DataColumn(ft.Text("TOTAL"), numeric=True),
                ft.DataColumn(ft.Text("AÇÕES")),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.WHITE,
            expand=True
        )

        self.content = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("Registrar Item", size=20, weight="bold", color=ft.Colors.BLUE_GREY_800),
                    ft.Divider(),
                    ft.Row([self.txt_codigo, self.txt_qtd]),
                    self.card_preview,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Adicionar Item", icon=ft.Icons.ADD_SHOPPING_CART, 
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, padding=20, shape=ft.RoundedRectangleBorder(radius=8)),
                        width=300, on_click=self._adicionar_item
                    ),
                ]), expand=1, padding=30, bgcolor=ft.Colors.WHITE, border_radius=15
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Text("Carrinho", size=20, weight="bold"), self.txt_itens_qtd], alignment="spaceBetween"),
                    ft.Divider(),
                    ft.Container(self.tabela_carrinho, expand=True, border=ft.border.all(1, "#e5e7eb"), border_radius=8),
                    ft.Divider(),
                    ft.Row([ft.Text("Total:", size=18, weight="bold"), self.txt_total], alignment="spaceBetween"),
                    ft.ElevatedButton(
                        "FINALIZAR VENDA", icon=ft.Icons.CHECK_CIRCLE,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, padding=20, shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=self._abrir_checkout, expand=True
                    )
                ]), expand=2, padding=30, bgcolor=ft.Colors.WHITE, border_radius=15
            )
        ], spacing=20, expand=True)

    # --- FUNÇÕES DE AUXÍLIO ---
    def _btn_pagamento(self, icon, text, selected):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=ft.Colors.BLUE_700 if selected else ft.Colors.GREY),
                ft.Text(text, size=10, color=ft.Colors.BLUE_900 if selected else ft.Colors.GREY)
            ], 
            spacing=2, 
            alignment=ft.MainAxisAlignment.CENTER # Se este der erro, use "center"
            ),
            padding=10, 
            border=ft.border.all(2 if selected else 1, ft.Colors.BLUE_600 if selected else ft.Colors.GREY_300),
            border_radius=8, 
            bgcolor=ft.Colors.BLUE_50 if selected else ft.Colors.WHITE,
            width=80, 
            height=70, 
            # SOLUÇÃO REAL: Coordenadas (0,0) significam centro absoluto.
            alignment=ft.Alignment(0, 0) 
        )
    def _notificar(self, msg, sucesso):
        self.main_page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="green" if sucesso else "red")
        self.main_page.snack_bar.open = True
        self.main_page.update()

    # --- LÓGICA DO CARRINHO ---
    def _atualizar_ui_carrinho(self):
        self.tabela_carrinho.rows.clear()
        total = Decimal("0")
        itens = 0
        for i, item in enumerate(self.carrinho):
            p = item['prod']
            q = item['qtd']
            subtotal = p.price * q
            total += subtotal
            itens += q
            
            btn_edit = ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, data=i, on_click=self._abrir_modal_editar)
            btn_delete = ft.IconButton(ft.Icons.DELETE, icon_color="red", data=i, on_click=self._preparar_remover_item)
            
            self.tabela_carrinho.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p.name)), ft.DataCell(ft.Text(str(q))),
                    ft.DataCell(ft.Text(f"R$ {p.price:.2f}")), ft.DataCell(ft.Text(f"R$ {subtotal:.2f}", weight="bold")),
                    ft.DataCell(ft.Row([btn_edit, btn_delete], spacing=0)),
                ])
            )
        self.txt_total.value = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.txt_itens_qtd.value = f"{itens} itens"
        self.update()

    def _adicionar_item(self, e):
        codigo = self.txt_codigo.value
        if not codigo: 
            return
            
        try:
            qtd_nova = int(self.txt_qtd.value)
            if qtd_nova <= 0: 
                raise ValueError
        except:
            self._notificar("Qtd inválida", False)
            return

        # Busca o produto no estoque
        produto = next((p for p in self.lista_produtos if p.barcode == codigo), None)
        if not produto:
            self._notificar("Produto não encontrado", False)
            return
        
        # --- LÓGICA DE AGRUPAMENTO (SÊNIOR) ---
        # Verifica se o produto já está no carrinho
        item_existente = next((item for item in self.carrinho if item['prod'].barcode == codigo), None)

        if item_existente:
            # Se já existe, apenas soma a nova quantidade
            item_existente['qtd'] += qtd_nova
            self._notificar(f"Quantidade atualizada: {produto.name}", True)
        else:
            # Se não existe, adiciona uma nova linha normalmente
            self.carrinho.append({'prod': produto, 'qtd': qtd_nova})
            self._notificar(f"Adicionado: {produto.name}", True)
        
        # Limpeza e atualização da UI
        self._atualizar_ui_carrinho()
        self.txt_codigo.value = ""
        self.txt_qtd.value = "1" # Reseta a quantidade para o próximo item
        self.card_preview.visible = False
        self.txt_codigo.focus()
        self.update()

    # --- MODAL REMOVER ITEM ---
    def _preparar_remover_item(self, e):
        self.item_para_remover_index = e.control.data
        self.dialog_delete.open = True
        self.page.update()

    def _fechar_modal_delete(self, e):
        self.dialog_delete.open = False
        self.page.update()

    def _confirmar_remover_item(self, e):
        if self.item_para_remover_index is not None:
            del self.carrinho[self.item_para_remover_index]
            self._atualizar_ui_carrinho()
            self._notificar("Item removido.", True)
        self._fechar_modal_delete(None)

    # --- MODAL EDITAR ---
    def _abrir_modal_editar(self, e):
        index = e.control.data
        self.item_para_editar_index = index
        self.txt_edit_qtd.value = str(self.carrinho[index]['qtd'])
        self.dialog_edit.open = True
        self.page.update()

    def _fechar_modal_edit(self, e):
        self.dialog_edit.open = False
        self.page.update()

    def _salvar_edicao_item(self, e):
        try:
            self.carrinho[self.item_para_editar_index]['qtd'] = int(self.txt_edit_qtd.value)
            self._atualizar_ui_carrinho()
            self._fechar_modal_edit(None)
        except: self._notificar("Erro ao editar", False)

    # --- CHECKOUT E IMPRESSÃO ---
    def _abrir_checkout(self, e):
        if not self.carrinho: return
        total = sum(i['prod'].price * i['qtd'] for i in self.carrinho)
        self.txt_checkout_total.value = f"R$ {total:.2f}"
        self.dialog_checkout.open = True
        self.page.update()

    def _fechar_modal_checkout(self, e):
        self.dialog_checkout.open = False
        self.page.update()

    def _efetivar_venda_backend(self, e):
        try:
            payload = [{'barcode': i['prod'].barcode, 'quantity': i['qtd']} for i in self.carrinho]
            self.sale_service.create_sale(payload)
            if self.switch_imprimir.value: self._imprimir_cupom()
            self._fechar_modal_checkout(None)
            self.carrinho = []; self._atualizar_ui_carrinho()
            self._notificar("Venda Confirmada!", True)
        except Exception as ex: self._notificar(f"Erro: {ex}", False)

    def _imprimir_cupom(self):
        filename = "cupom_fiscal.txt"
        try:
            # Tenta buscar as configurações da empresa (Nome e Rodapé)
            config = self.settings_service.get_settings()
            company_name = config.company_name if config else "MINHA EMPRESA"
            receipt_footer = config.receipt_footer if config else "Obrigado pela preferência!"
            
            with open(filename, "w", encoding="utf-8") as f:
                # Cabeçalho centralizado (32 colunas é o padrão para térmicas de 58mm)
                f.write(f"{company_name:^32}\n")
                f.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^32}\n")
                f.write("-" * 32 + "\n")
                f.write(f"{'ITEM':<18} {'QTD':<5} {'TOTAL':>7}\n")
                f.write("-" * 32 + "\n")
                
                total_venda = Decimal("0")
                for item in self.carrinho:
                    p = item['prod']
                    q = item['qtd']
                    subtotal = p.price * q
                    total_venda += subtotal
                    # Nome do produto limitado a 18 caracteres para não quebrar a linha
                    f.write(f"{p.name[:18]:<18} {q:<5} {subtotal:>7.2f}\n")
                
                f.write("-" * 32 + "\n")
                f.write(f"{'TOTAL R$':<18} {total_venda:>13.2f}\n")
                f.write("-" * 32 + "\n")
                f.write(f"{receipt_footer:^32}\n\n\n\n\n") # Espaço para o corte de papel
            
            # Comando para enviar ao Bloco de Notas e imprimir direto na padrão
            # O parâmetro /p envia para a impressora padrão do Windows
            subprocess.run(["notepad", "/p", filename], shell=True)
            
        except Exception as ex:
            print(f"Erro na impressão: {ex}")
            self._notificar("Erro ao gerar cupom!", False)

    def _buscar_preview(self, e):
        p = next((p for p in self.lista_produtos if p.barcode == self.txt_codigo.value), None)
        if p:
            self.info_preview_nome.value = p.name
            self.info_preview_preco.value = f"R$ {p.price:.2f}"
            self.card_preview.visible = True
        else: self.card_preview.visible = False
        self.update()