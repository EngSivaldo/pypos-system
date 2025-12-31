# Tela principal da aplicação

import flet as ft
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.config.settings import DATABASE_URL
from src.services.product_service import ProductService

def main(page: ft.Page):
    # --- Configuração da Janela ---
    page.title = "PyPOS - Sistema Sênior"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 600
    
    # --- Injeção de Dependência (Setup do Backend) ---
    engine = create_engine(DATABASE_URL)
    session = Session(engine)
    service = ProductService(session)

    # --- Elementos da UI ---
    txt_titulo = ft.Text("Gestão de Produtos", size=24, weight="bold")
    
    # Tabela de Dados (DataTablet)
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Preço"), numeric=True),
            ft.DataColumn(ft.Text("Estoque"), numeric=True),
        ],
        rows=[]
    )

    def carregar_dados():
        """Busca dados do banco e popula a tabela"""
        tabela.rows.clear()
        produtos = service.list_products()
        
        for p in produtos:
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p.barcode)),
                        ft.DataCell(ft.Text(p.name)),
                        ft.DataCell(ft.Text(f"R$ {p.price:.2f}")),
                        ft.DataCell(ft.Text(str(p.stock_quantity))),
                    ]
                )
            )
        page.update()

    # --- Montagem da Tela ---
    # Botão para recarregar (Simulando uma ação)
    btn_refresh = ft.ElevatedButton("Atualizar Lista", on_click=lambda e: carregar_dados())

    page.add(
        ft.Column([
            txt_titulo,
            ft.Divider(),
            btn_refresh,
            tabela
        ])
    )

    # Carga inicial
    carregar_dados()

if __name__ == "__main__":
    ft.app(target=main)