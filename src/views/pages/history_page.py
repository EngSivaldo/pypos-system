import flet as ft
from datetime import datetime
import os
import subprocess

class HistoryPage(ft.Container):
    def __init__(self, page, sale_service):
        super().__init__()
        self.main_page = page
        self.sale_service = sale_service
        
        self.expand = True
        self.padding = 20
        self.bgcolor = "#f3f4f6"

        # Variável para guardar a venda que está sendo visualizada no modal
        self.venda_selecionada = None

        # --- Tabela de Vendas ---
        self.tabela_vendas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("DATA/HORA")),
                ft.DataColumn(ft.Text("ID VENDA")),
                ft.DataColumn(ft.Text("TOTAL"), numeric=True),
                ft.DataColumn(ft.Text("DETALHES")),
            ],
            rows=[],
            border=ft.Border.all(1, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.WHITE,
            expand=True
        )

        # --- Modal de Detalhes ---
        self.lista_itens_modal = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)
        self.txt_total_modal = ft.Text("R$ 0,00", weight="bold", size=20)
        
        self.dialog_detalhes = ft.AlertDialog(
            title=ft.Text("Detalhes da Venda"),
            content=ft.Container(
                width=400,
                content=ft.Column([
                    ft.Text("Itens Comprados:", weight="bold"),
                    ft.Divider(),
                    self.lista_itens_modal,
                    ft.Divider(),
                    ft.Row([ft.Text("Total Final:", size=16), self.txt_total_modal], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], tight=True)
            ),
            actions=[
                ft.TextButton("Fechar", on_click=self._fechar_modal),
                ft.FilledButton("Reimprimir Cupom", icon=ft.Icons.PRINT, on_click=self._reimprimir_cupom)
            ]
        )
        # Adiciona ao overlay para garantir que abra
        self.main_page.overlay.append(self.dialog_detalhes)

        # --- Layout Principal ---
        self.content = ft.Column([
            ft.Text("Histórico de Vendas", size=28, weight="bold", color=ft.Colors.BLUE_GREY_900),
            ft.Text("Consulte transações passadas.", size=14, color=ft.Colors.GREY_600),
            ft.Divider(color="transparent", height=20),
            
            ft.Container(
                content=self.tabela_vendas,
                bgcolor=ft.Colors.WHITE,
                padding=10,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                expand=True
            )
        ], expand=True)

    def did_mount(self):
        """Carrega os dados assim que a tela aparece"""
        self.carregar_dados()

    def carregar_dados(self):
        self.tabela_vendas.rows.clear()
        try:
            vendas = self.sale_service.list_sales()
            
            for venda in vendas:
                # Formata Data
                data_fmt = venda.created_at.strftime("%d/%m/%Y %H:%M")
                
                # Botão de Detalhes
                btn_detalhes = ft.IconButton(
                    icon=ft.Icons.VISIBILITY,
                    icon_color=ft.Colors.BLUE,
                    data=venda, # Guardamos o objeto Venda inteiro aqui
                    on_click=self._abrir_detalhes
                )

                self.tabela_vendas.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(data_fmt)),
                        ft.DataCell(ft.Text(venda.id[:8] + "...")), # Mostra só o começo do UUID
                        ft.DataCell(ft.Text(f"R$ {venda.total_amount:.2f}")),
                        ft.DataCell(btn_detalhes),
                    ])
                )
            self.update()
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")

    def _abrir_detalhes(self, e):
        self.venda_selecionada = e.control.data # Recupera a venda
        
        # Limpa e preenche a lista de itens do modal
        self.lista_itens_modal.controls.clear()
        
        for item in self.venda_selecionada.items:
            # item.product é carregado pelo relacionamento do SQLAlchemy
            texto_item = f"{item.quantity}x {item.product.name} (R$ {item.unit_price:.2f})"
            subtotal = f"R$ {item.quantity * item.unit_price:.2f}"
            
            row = ft.Row([
                ft.Text(texto_item, size=12, expand=True),
                ft.Text(subtotal, size=12, weight="bold")
            ])
            self.lista_itens_modal.controls.append(row)

        self.txt_total_modal.value = f"R$ {self.venda_selecionada.total_amount:.2f}"
        
        self.dialog_detalhes.open = True
        self.main_page.update()

    def _fechar_modal(self, e):
        self.dialog_detalhes.open = False
        self.main_page.update()

    def _reimprimir_cupom(self, e):
        if not self.venda_selecionada: return
        
        filename = "reimpressao_cupom.txt"
        try:
            venda = self.venda_selecionada
            with open(filename, "w", encoding="utf-8") as f:
                f.write("="*32 + "\n")
                f.write("      PYPOS (REIMPRESSAO)      \n")
                f.write("="*32 + "\n")
                f.write(f"DATA: {venda.created_at.strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("-" * 32 + "\n")
                f.write(f"{'ITEM':<18} {'QTD':<5} {'TOTAL':<7}\n")
                f.write("-" * 32 + "\n")
                
                for item in venda.items:
                    nome = item.product.name[:18]
                    qtd = item.quantity
                    valor = item.unit_price * qtd
                    f.write(f"{nome:<18} {qtd:<5} {valor:<7.2f}\n")
                
                f.write("-" * 32 + "\n")
                f.write(f"TOTAL:              R$ {venda.total_amount:.2f}\n")
                f.write("="*32 + "\n\n\n")

            # Tenta imprimir (Mesma lógica do PDV)
            subprocess.run(["notepad", "/p", filename], shell=True)
            
            # Fecha modal e avisa
            self._fechar_modal(None)
            snack = ft.SnackBar(ft.Text("Enviado para impressão!"), bgcolor="green")
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()

        except Exception as ex:
            print(f"Erro impressão: {ex}")
            os.startfile(filename) # Fallback