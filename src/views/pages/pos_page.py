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
        self.padding = 25
        
        # === TEMA VISUAL PADRÃO ===
        self.COLOR_PRIMARY = ft.Colors.BLUE_ACCENT_700
        self.COLOR_SUCCESS = ft.Colors.GREEN_600
        self.COLOR_DANGER = ft.Colors.RED_600
        self.COLOR_BG = "#F8FAFC"
        self.COLOR_CARD = ft.Colors.WHITE
        self.COLOR_TEXT = ft.Colors.BLUE_GREY_900
        self.COLOR_MUTED = ft.Colors.BLUE_GREY_400
        
        self.bgcolor = self.COLOR_BG

        self.carrinho = [] 
        self.item_para_editar_index = None 
        self.item_para_remover_index = None 
        
        # Variável de controle de pagamento
        self.forma_pagamento_selecionada = "Dinheiro"

        try:
            self.lista_produtos = self.product_service.list_products()
        except Exception:
            self.lista_produtos = []

        # --- MODAL BUSCA POR PRODUTO ---
        self.txt_busca_nome = ft.TextField(
            label="Pesquisar por início do nome...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=15,
            border_color=self.COLOR_PRIMARY,
            on_change=self._filtrar_busca_avancada,
            text_style=ft.TextStyle(weight="bold")
        )
        self.lista_resultados_busca = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=350)
        
        self.dialog_busca = ft.AlertDialog(
            title=ft.Text("Buscar Produto 🔍", weight="bold", color=self.COLOR_TEXT),
            content=ft.Container(
                content=ft.Column([self.txt_busca_nome, ft.Divider(), self.lista_resultados_busca], tight=True),
                width=550
            ),
            shape=ft.RoundedRectangleBorder(radius=20)
        )
        self.main_page.overlay.append(self.dialog_busca)

        # --- MODAL CONFIRMAR REMOÇÃO ---
        self.dialog_delete = ft.AlertDialog(
            modal=True,
            title=ft.Text("Remover Item?", color=self.COLOR_TEXT, weight="bold"),
            content=ft.Text("Deseja realmente retirar este produto do carrinho?", color=self.COLOR_TEXT),
            actions=[
                ft.TextButton("Voltar", on_click=self._fechar_modal_delete),
                ft.ElevatedButton("Confirmar", bgcolor=self.COLOR_DANGER, color=ft.Colors.WHITE, on_click=self._confirmar_remover_item)
            ],
            shape=ft.RoundedRectangleBorder(radius=15)
        )
        self.main_page.overlay.append(self.dialog_delete)

        # --- MODAL EDITAR QUANTIDADE ---
        self.txt_edit_qtd = ft.TextField(
            label="Nova Qtd", 
            autofocus=True, 
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10
        )
        self.dialog_edit = ft.AlertDialog(
            modal=True, 
            title=ft.Text("Editar Item", weight="bold"), 
            content=self.txt_edit_qtd,
            actions=[
                ft.TextButton("Cancelar", on_click=self._fechar_modal_edit),
                ft.FilledButton("Salvar", on_click=self._salvar_edicao_item)
            ],
            shape=ft.RoundedRectangleBorder(radius=15)
        )
        self.main_page.overlay.append(self.dialog_edit)

        # --- MODAL CHECKOUT (CONCLUIR VENDA) ---
        self.txt_checkout_total = ft.Text("R$ 0,00", size=45, weight="black", color=self.COLOR_SUCCESS)
        
        self.txt_valor_recebido = ft.TextField(
            label="VALOR RECEBIDO", 
            prefix=ft.Text("R$ ", size=20, weight="bold"),
            text_size=24,
            text_style=ft.TextStyle(weight="bold", color=self.COLOR_PRIMARY),
            border_color=self.COLOR_PRIMARY,
            on_change=self._calcular_troco,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.txt_troco_exibir = ft.Text("TROCO: R$ 0,00", size=24, weight="bold", color=self.COLOR_SUCCESS)
        self.switch_imprimir = ft.Switch(label="Emitir Cupom Fiscal", value=True, active_color=self.COLOR_PRIMARY)

        # Container para os botões de pagamento que serão atualizados dinamicamente
        self.row_pagamentos = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        self.dialog_checkout = ft.AlertDialog(
            modal=True,
            title=ft.Text("Finalizar Venda 🛒", weight="bold", size=22, color=self.COLOR_TEXT),
            content=ft.Column([
                ft.Divider(),
                ft.Row([ft.Text("TOTAL A PAGAR:", weight="bold"), self.txt_checkout_total], alignment="spaceBetween"),
                ft.Container(height=10),
                self.txt_valor_recebido,
                ft.Container(content=self.txt_troco_exibir, alignment=ft.alignment.Alignment(0, 0), padding=10),
                ft.Divider(),
                ft.Text("MÉTODO DE PAGAMENTO", size=12, weight="bold", color=self.COLOR_MUTED),
                self.row_pagamentos, # Inserção dinâmica dos botões
            ], tight=True, width=420),
            actions=[
                ft.TextButton("CANCELAR", on_click=self._fechar_modal_checkout, style=ft.ButtonStyle(color=self.COLOR_DANGER)),
                ft.ElevatedButton("CONFIRMAR PAGAMENTO", icon=ft.Icons.CHECK, on_click=self._efetivar_venda_backend, 
                                  style=ft.ButtonStyle(bgcolor=self.COLOR_SUCCESS, color=ft.Colors.WHITE, padding=20))
            ],
            shape=ft.RoundedRectangleBorder(radius=20)
        )
        self.main_page.overlay.append(self.dialog_checkout)

        # --- UI ELEMENTS (LADO ESQUERDO) ---
        self.info_preview_nome = ft.Text("-", size=18, weight="bold", color=self.COLOR_TEXT)
        self.info_preview_preco = ft.Text("R$ 0,00", size=24, weight="black", color=self.COLOR_SUCCESS)
        
        self.card_preview = ft.Container(
            visible=False,
            bgcolor=self.COLOR_CARD,
            padding=22,
            border_radius=18,
            border=ft.border.all(1, ft.Colors.BLUE_100),
            shadow=ft.BoxShadow(blur_radius=25, spread_radius=1, color="#00000012", offset=ft.Offset(0, 6)),
            content=ft.Column([
                ft.Text("PRODUTO IDENTIFICADO", size=10, weight="bold", color=self.COLOR_MUTED),
                self.info_preview_nome,
                self.info_preview_preco
            ], spacing=4)
        )

        self.txt_codigo = ft.TextField(
            label="Código ou Nome do Produto", autofocus=True, prefix_icon=ft.Icons.SEARCH,
            border_radius=12, text_size=16, border_color=self.COLOR_MUTED,
            focused_border_color=self.COLOR_PRIMARY,
            on_submit=self._adicionar_item, on_change=self._buscar_preview, 
            expand=True
        )
        
        self.txt_qtd = ft.TextField(
            label="Qtd", value="1", width=90, border_radius=12, 
            text_align=ft.TextAlign.CENTER, text_size=16, border_color=self.COLOR_MUTED
        )
        
        self.txt_total = ft.Text("R$ 0,00", size=52, weight="black", color=self.COLOR_TEXT)
        self.txt_itens_qtd = ft.Text("0 itens", size=16, weight="bold", color=ft.Colors.WHITE)
        
        self.tabela_carrinho = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("PRODUTO", weight="bold", color=self.COLOR_TEXT)),
                ft.DataColumn(ft.Text("QTD", weight="bold", color=self.COLOR_TEXT), numeric=True),
                ft.DataColumn(ft.Text("UNIT.", weight="bold", color=self.COLOR_TEXT), numeric=True),
                ft.DataColumn(ft.Text("TOTAL", weight="bold", color=self.COLOR_TEXT), numeric=True),
                ft.DataColumn(ft.Text("AÇÕES", weight="bold", color=self.COLOR_TEXT)),
            ],
            rows=[],
            heading_row_color=ft.Colors.BLUE_GREY_50,
            expand=True,
            column_spacing=15
        )

        # === LAYOUT PRINCIPAL COM DESTAQUE NO CARRINHO ===
        self.content = ft.Row([
            # Coluna Esquerda: Registro
            ft.Container(
                content=ft.Column([
                    ft.Text("REGISTRAR ITEM", size=22, weight="black", color=self.COLOR_TEXT),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Row([self.txt_codigo, self.txt_qtd], spacing=10),
                    self.card_preview,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "ADICIONAR",
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        height=50,
                        style=ft.ButtonStyle(
                            bgcolor=self.COLOR_PRIMARY, color=ft.Colors.WHITE,
                            elevation=6, shape=ft.RoundedRectangleBorder(radius=14),
                            text_style=ft.TextStyle(size=14, weight="bold")
                        ),
                        on_click=self._adicionar_item, expand=True
                    ),
                    ft.OutlinedButton(
                        "PESQUISAR NO CATÁLOGO", icon=ft.Icons.SEARCH_SHARP, height=45,
                        on_click=self._abrir_busca,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            color=self.COLOR_PRIMARY,
                        )
                    ),
                ], spacing=15),
                width=350, padding=30, bgcolor=self.COLOR_CARD, border_radius=25,
                shadow=ft.BoxShadow(blur_radius=20, color="#00000005")
            ),
            
            # Coluna Direita: Carrinho
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("CARRINHO", size=22, weight="black", color=self.COLOR_TEXT),
                        ft.Container(content=self.txt_itens_qtd, padding=12, bgcolor=ft.Colors.BLUE_50, border_radius=12)
                    ], alignment="spaceBetween"),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Container(
                        content=ft.Column([self.tabela_carrinho], scroll=ft.ScrollMode.AUTO),
                        expand=True, border=ft.border.all(2.5, self.COLOR_PRIMARY), border_radius=20,
                        bgcolor=ft.Colors.WHITE, padding=10,
                        shadow=ft.BoxShadow(blur_radius=30, color="#00000010", offset=ft.Offset(0, 10))
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Row([
                        ft.Text("VALOR TOTAL:", size=18, weight="bold", color=self.COLOR_MUTED),
                        self.txt_total
                    ], alignment="spaceBetween"),
                    ft.ElevatedButton(
                        "FINALIZAR VENDA", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, height=65,
                        style=ft.ButtonStyle(
                            bgcolor=self.COLOR_SUCCESS, color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=18),
                            text_style=ft.TextStyle(size=20, weight="black")
                        ),
                        on_click=self._abrir_checkout, expand=True
                    )
                ], spacing=15),
                expand=True, padding=35, bgcolor=self.COLOR_CARD, border_radius=25,
                shadow=ft.BoxShadow(blur_radius=30, color="#00000008")
            )
        ], spacing=25, expand=True)

    # --- LÓGICA DE PAGAMENTO ---
    def _selecionar_pagamento(self, forma):
        self.forma_pagamento_selecionada = forma
        total_venda = sum(item['prod'].price * item['qtd'] for item in self.carrinho)
        
        # Se for Cartão ou Pix, não existe troco, preenche tudo
        if forma in ["Crédito", "Débito", "Pix"]:
            self.txt_valor_recebido.value = str(total_venda)
            self.txt_valor_recebido.read_only = True
        else:
            self.txt_valor_recebido.value = ""
            self.txt_valor_recebido.read_only = False
            
        self._atualizar_botoes_pagamento()
        self._calcular_troco(None)

    def _atualizar_botoes_pagamento(self):
        self.row_pagamentos.controls = [
            self._btn_pagamento(ft.Icons.MONEY, "Dinheiro", self.forma_pagamento_selecionada == "Dinheiro"),
            self._btn_pagamento(ft.Icons.CREDIT_CARD, "Crédito", self.forma_pagamento_selecionada == "Crédito"),
            self._btn_pagamento(ft.Icons.CREDIT_CARD, "Débito", self.forma_pagamento_selecionada == "Débito"),
            self._btn_pagamento(ft.Icons.PHONELINK_RING, "Pix", self.forma_pagamento_selecionada == "Pix"),
        ]
        self.dialog_checkout.update()

    def _btn_pagamento(self, icon, text, selected):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=32, color=self.COLOR_PRIMARY if selected else ft.Colors.BLUE_GREY_300),
                ft.Text(text, size=11, weight="bold", color=self.COLOR_TEXT if selected else ft.Colors.BLUE_GREY_400),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            padding=15, width=105, height=95, border_radius=16,
            bgcolor=ft.Colors.BLUE_50 if selected else self.COLOR_CARD,
            border=ft.border.all(2, self.COLOR_PRIMARY if selected else ft.Colors.BLUE_GREY_200),
            shadow=ft.BoxShadow(blur_radius=15, color="#00000010", offset=ft.Offset(0, 4)),
            alignment=ft.alignment.Alignment(0, 0),
            on_click=lambda _: self._selecionar_pagamento(text)
        )

    # --- LÓGICA DE TROCO ---
    def _calcular_troco(self, e):
        try:
            total = sum(item['prod'].price * item['qtd'] for item in self.carrinho)
            recebido_str = self.txt_valor_recebido.value.replace(",", ".")
            recebido = Decimal(recebido_str) if recebido_str else Decimal("0")
            troco = recebido - total
            if troco >= 0:
                self.txt_troco_exibir.value = f"TROCO: R$ {troco:.2f}"
                self.txt_troco_exibir.color = self.COLOR_SUCCESS
            else:
                self.txt_troco_exibir.value = f"FALTANDO: R$ {abs(troco):.2f}"
                self.txt_troco_exibir.color = self.COLOR_DANGER
            self.dialog_checkout.update()
        except: pass

    # --- IDENTIFICAÇÃO E BUSCA ---
    def _identificar_produto(self, termo):
        termo = termo.lower().strip()
        if not termo: return None
        for p in self.lista_produtos:
            if p.barcode.lower() == termo: return p
        for p in self.lista_produtos:
            if p.name.lower().startswith(termo): return p
        return None

    def _buscar_preview(self, e):
        p = self._identificar_produto(self.txt_codigo.value)
        if p:
            self.info_preview_nome.value = p.name.upper()
            self.info_preview_preco.value = f"R$ {p.price:.2f}"
            self.card_preview.visible = True
        else: self.card_preview.visible = False
        self.update()

    def _adicionar_item(self, e):
        produto = self._identificar_produto(self.txt_codigo.value)
        if not produto:
            self._notificar("Produto não encontrado", False)
            return
        try:
            qtd_nova = int(self.txt_qtd.value)
            if qtd_nova <= 0: raise ValueError
            item_existente = next((item for item in self.carrinho if item['prod'].barcode == produto.barcode), None)
            if item_existente: item_existente['qtd'] += qtd_nova
            else: self.carrinho.append({'prod': produto, 'qtd': qtd_nova})
            self._atualizar_ui_carrinho()
            self.txt_codigo.value = ""; self.txt_qtd.value = "1"; self.card_preview.visible = False
            self._resetar_foco()
            self.update()
        except: self._notificar("Qtd inválida", False)

    def _atualizar_ui_carrinho(self):
        self.tabela_carrinho.rows.clear()
        total = Decimal("0"); itens = 0
        for i, item in enumerate(self.carrinho):
            p, q = item['prod'], item['qtd']
            subtotal = p.price * q
            total += subtotal; itens += q
            btn_edit = ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=self.COLOR_PRIMARY, data=i, on_click=self._abrir_modal_editar)
            btn_delete = ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=self.COLOR_DANGER, data=i, on_click=self._preparar_remover_item)
            self.tabela_carrinho.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p.name.upper(), weight="w600", color=self.COLOR_TEXT)), 
                    ft.DataCell(ft.Text(str(q), color=self.COLOR_TEXT, weight="bold")),
                    ft.DataCell(ft.Text(f"R$ {p.price:.2f}", color=self.COLOR_TEXT)), 
                    ft.DataCell(ft.Text(f"R$ {subtotal:.2f}", weight="black", color=self.COLOR_PRIMARY)),
                    ft.DataCell(ft.Row([btn_edit, btn_delete], spacing=0)),
                ])
            )
        self.txt_total.value = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.txt_itens_qtd.value = f"{itens} itens"; self.update()

    # --- FINALIZAÇÃO E BACKEND ---
    def _abrir_checkout(self, e):
        if not self.carrinho: return
        self.forma_pagamento_selecionada = "Dinheiro"
        self._atualizar_botoes_pagamento()
        self.txt_valor_recebido.value = ""
        self.txt_valor_recebido.read_only = False
        self.txt_troco_exibir.value = "TROCO: R$ 0,00"
        total = sum(i['prod'].price * i['qtd'] for i in self.carrinho)
        self.txt_checkout_total.value = f"R$ {total:.2f}"
        self.dialog_checkout.open = True; self.main_page.update()

    def _efetivar_venda_backend(self, e):
        try:
            total = sum(i['prod'].price * i['qtd'] for i in self.carrinho)
            recebido = Decimal(self.txt_valor_recebido.value.replace(",", ".") if self.txt_valor_recebido.value else "0")
            if recebido < total:
                self._notificar("VALOR RECEBIDO INSUFICIENTE", False)
                return
            payload = [{'barcode': i['prod'].barcode, 'quantity': i['qtd']} for i in self.carrinho]
            self.sale_service.create_sale(payload)
            if self.switch_imprimir.value: self._imprimir_cupom(recebido)
            self.dialog_checkout.open = False
            self.carrinho = []; self._atualizar_ui_carrinho()
            self._notificar("Venda Concluída!", True)
            self._resetar_foco()
        except Exception as ex: self._notificar(f"Erro: {ex}", False)

    def _imprimir_cupom(self, recebido):
        filename = "cupom_fiscal.txt"
        try:
            config = self.settings_service.get_settings()
            company_name = config.company_name if config else "MINHA EMPRESA"
            total = sum(i['prod'].price * i['qtd'] for i in self.carrinho)
            LARGURA = 48 
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"{company_name.upper():^{LARGURA}}\n")
                f.write(f"{'EXTRATO DE VENDA':^{LARGURA}}\n")
                f.write("-" * LARGURA + "\n")
                f.write(f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("-" * LARGURA + "\n")
                f.write(f"{'DESCRIÇÃO':<20} {'QTD':<6} {'UNIT':<10} {'TOTAL':>9}\n")
                for item in self.carrinho:
                    p, q = item['prod'], item['qtd']
                    f.write(f"{p.name[:19].upper():<20} {q:<6} {p.price:<10.2f} {(p.price*q):>9.2f}\n")
                f.write("-" * LARGURA + "\n")
                f.write(f"{'TOTAL R$:':<30} {total:>17.2f}\n")
                f.write(f"{'PAGAMENTO:':<30} {self.forma_pagamento_selecionada.upper():>17}\n")
                f.write(f"{'RECEBIDO R$:':<30} {recebido:>17.2f}\n")
                f.write(f"{'TROCO R$:':<30} {(recebido-total):>17.2f}\n")
                f.write("-" * LARGURA + "\n")
            subprocess.run(["notepad", "/p", filename], shell=True)
        except Exception as ex: print(f"Erro na impressão: {ex}")

    # --- AUXILIARES ---
    def _notificar(self, msg, sucesso):
        self.main_page.snack_bar = ft.SnackBar(ft.Text(msg.upper(), weight="bold"), bgcolor=self.COLOR_SUCCESS if sucesso else self.COLOR_DANGER)
        self.main_page.snack_bar.open = True; self.main_page.update()

    def _resetar_foco(self):
        if self.txt_codigo.page:
            try: self.txt_codigo.focus(); self.txt_codigo.update()
            except: pass

    def _abrir_busca(self, e): self.dialog_busca.open = True; self.main_page.update()
    def _fechar_busca(self): self.dialog_busca.open = False; self.main_page.update()
    def _filtrar_busca_avancada(self, e):
        t = self.txt_busca_nome.value.lower()
        self.lista_resultados_busca.controls.clear()
        if not t: self.update(); return
        for p in self.lista_produtos:
            if p.name.lower().startswith(t):
                self.lista_resultados_busca.controls.append(ft.ListTile(title=ft.Text(p.name.upper(), weight="bold"), trailing=ft.ElevatedButton("Escolher", on_click=lambda _, prod=p: self._selecionar_da_busca(prod))))
        self.update()

    def _selecionar_da_busca(self, p): self.txt_codigo.value = p.barcode; self.dialog_busca.open = False; self._buscar_preview(None)
    def _fechar_modal_checkout(self, e): self.dialog_checkout.open = False; self.main_page.update()
    def _preparar_remover_item(self, e): self.item_para_remover_index = e.control.data; self.dialog_delete.open = True; self.main_page.update()
    def _fechar_modal_delete(self, e): self.dialog_delete.open = False; self.main_page.update()
    def _confirmar_remover_item(self, e):
        if self.item_para_remover_index is not None: del self.carrinho[self.item_para_remover_index]; self._atualizar_ui_carrinho()
        self._fechar_modal_delete(None)
    def _abrir_modal_editar(self, e): self.item_para_editar_index = e.control.data; self.txt_edit_qtd.value = str(self.carrinho[self.item_para_editar_index]['qtd']); self.dialog_edit.open = True; self.main_page.update()
    def _fechar_modal_edit(self, e): self.dialog_edit.open = False; self.main_page.update()
    def _salvar_edicao_item(self, e):
        try: self.carrinho[self.item_para_editar_index]['qtd'] = int(self.txt_edit_qtd.value); self._atualizar_ui_carrinho(); self._fechar_modal_edit(None)
        except: self._notificar("Erro ao editar", False)