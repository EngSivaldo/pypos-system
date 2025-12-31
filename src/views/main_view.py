import flet as ft
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.config.settings import DATABASE_URL
from src.services.product_service import ProductService

def main(page: ft.Page):
    # --- 1. Configuração Global ---
    page.title = "PyPOS | Sistema Sênior"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.window_min_width = 1000
    page.window_min_height = 700

    print("🚀 Sistema iniciado...")

    # --- 2. Setup do Backend ---
    try:
        engine = create_engine(DATABASE_URL)
        session = Session(engine)
        service = ProductService(session)
        print("✅ Banco de dados conectado.")
    except Exception as e:
        print(f"❌ Erro ao conectar banco: {e}")

    # --- 3. Elementos da Tela de Estoque (Inputs) ---
    txt_nome = ft.TextField(label="Nome do Produto", border_color=ft.Colors.BLUE_GREY_400)
    txt_codigo = ft.TextField(label="Código de Barras", border_color=ft.Colors.BLUE_GREY_400)
    # FIX: prefix usando componente Text para evitar erro de versão
    txt_preco = ft.TextField(label="Preço", keyboard_type=ft.KeyboardType.NUMBER, prefix=ft.Text("R$ "), border_color=ft.Colors.BLUE_GREY_400)
    txt_estoque = ft.TextField(label="Qtd Inicial", value="0", keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.BLUE_GREY_400)

    # KPIs (Cards de Topo)
    txt_total_produtos = ft.Text("0", size=30, weight="bold", color=ft.Colors.WHITE)
    txt_valor_estoque = ft.Text("R$ 0,00", size=30, weight="bold", color=ft.Colors.WHITE)

    # Tabela de Dados
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("CÓDIGO", weight="bold")),
            ft.DataColumn(ft.Text("PRODUTO", weight="bold")),
            ft.DataColumn(ft.Text("PREÇO", weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("ESTOQUE", weight="bold"), numeric=True),
        ],
        rows=[],
        border=ft.Border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        heading_row_color=ft.Colors.GREY_200,
        expand=True
    )

    # --- 4. Lógica de Negócio ---
    def carregar_dados():
        print("🔄 Carregando dados...")
        tabela.rows.clear()
        try:
            produtos = service.list_products()
            for p in produtos:
                tabela.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(p.barcode, weight="bold")),
                        ft.DataCell(ft.Text(p.name)),
                        ft.DataCell(ft.Text(f"R$ {p.price:.2f}")),
                        ft.DataCell(ft.Container(
                            content=ft.Text(str(p.stock_quantity), color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.GREEN_600 if p.stock_quantity > 10 else ft.Colors.RED_400,
                            padding=5, border_radius=5
                        )),
                    ])
                )
            
            # Atualiza KPIs
            total_qtd = len(produtos)
            total_valor = sum(p.price * p.stock_quantity for p in produtos)
            txt_total_produtos.value = str(total_qtd)
            txt_valor_estoque.value = f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            page.update()
        except Exception as e:
            print(f"Erro ao ler dados: {e}")

    # Ação de fechar modal
    def fechar_modal_action(e):
        modal_cadastro.open = False
        page.update()

    # Ação de Salvar
    def salvar_produto(e):
        print("💾 Tentando salvar...")
        try:
            service.create_product(
                name=txt_nome.value,
                barcode=txt_codigo.value,
                price=txt_preco.value,
                stock=int(txt_estoque.value or 0)
            )
            
            # Fecha modal e recarrega
            modal_cadastro.open = False
            carregar_dados()
            mostrar_msg("Produto salvo!", True)
            
            # Limpa campos
            txt_nome.value = ""
            txt_codigo.value = ""
            txt_preco.value = ""
            txt_estoque.value = "0"
            page.update()
            
        except ValueError as erro:
            print(f"⚠️ Validação: {erro}")
            mostrar_msg(str(erro), False)
        except Exception as e:
            print(f"❌ Erro Crítico: {e}")

    def mostrar_msg(msg, sucesso=True):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN if sucesso else ft.Colors.RED)
        page.snack_bar.open = True
        page.update()

    # --- 5. Componentes Visuais ---
    
    # Modal (Definição)
    modal_cadastro = ft.AlertDialog(
        modal=True,
        title=ft.Text("Novo Produto"),
        content=ft.Column([txt_nome, txt_codigo, txt_preco, txt_estoque], tight=True, width=400),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_modal_action),
            # FIX: FilledButton é o padrão moderno, substitui ElevatedButton
            ft.FilledButton("Salvar", on_click=salvar_produto, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_800)),
        ],
    )

    def abrir_modal_click(e):
        print("🟢 Abrindo modal...")
        page.dialog = modal_cadastro
        modal_cadastro.open = True
        page.update()

    def criar_card(titulo, valor, icone, cor):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(icone, color=ft.Colors.WHITE, size=30), bgcolor=ft.Colors.WHITE24, padding=15, border_radius=10),
                ft.Column([ft.Text(titulo, color=ft.Colors.WHITE70, size=14), valor], spacing=2)
            ]),
            bgcolor=cor, padding=20, border_radius=15, expand=True, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        )

    # --- 6. Definição das Telas (Views) ---
    
    # 6.1 Dashboard
    view_dashboard = ft.Container(
        visible=False,
        content=ft.Column([
            ft.Text("Dashboard Geral", size=30, weight="bold", color=ft.Colors.BLUE_GREY_800),
            ft.Text("Gráficos e Estatísticas virão aqui...", color=ft.Colors.GREY),
            ft.Icon(ft.Icons.PIE_CHART, size=100, color=ft.Colors.BLUE_200)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment(0, 0), # FIX: Alignment explícito
        expand=True
    )

    # 6.2 Estoque (Principal)
    view_estoque = ft.Column([
        ft.Row([
            ft.Column([
                ft.Text("Gestão de Estoque", size=28, weight="bold", color=ft.Colors.BLUE_GREY_900),
                ft.Text("Gerencie seus produtos e preços", size=14, color=ft.Colors.GREY_600),
            ]),
            ft.FloatingActionButton(icon=ft.Icons.ADD, tooltip="Novo Produto", on_click=abrir_modal_click)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
        
        ft.Row([
            criar_card("Total Produtos", txt_total_produtos, ft.Icons.INVENTORY_2, ft.Colors.BLUE_700),
            criar_card("Valor Estoque", txt_valor_estoque, ft.Icons.MONETIZATION_ON, ft.Colors.GREEN_700),
        ], spacing=20),
        
        ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
        
        ft.Container(content=ft.Column([tabela], scroll=ft.ScrollMode.AUTO), bgcolor=ft.Colors.WHITE, border_radius=15, padding=10, expand=True, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12))
    ], visible=True, expand=True)

    # 6.3 Vendas
    view_vendas = ft.Container(
        visible=False,
        content=ft.Column([
            ft.Text("Frente de Caixa", size=30, weight="bold", color=ft.Colors.BLUE_GREY_800),
            ft.Text("Sistema de PDV em construção...", color=ft.Colors.GREY),
            ft.Icon(ft.Icons.POINT_OF_SALE, size=100, color=ft.Colors.GREEN_200)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment(0, 0), # FIX: Alignment explícito
        expand=True
    )

    # --- 7. Navegação Sênior (Fix Definitivo) ---
    def navegar(e):
        # Esconde todas
        view_dashboard.visible = False
        view_estoque.visible = False
        view_vendas.visible = False
        
        # SOLUÇÃO SÊNIOR: Usamos 'data' em vez de 'text'. 
        # 'text' pode falhar ou mudar. 'data' é constante.
        btn_id = e.control.data 
        print(f"👉 Navegando para ID: {btn_id}")

        if btn_id == "dashboard":
            view_dashboard.visible = True
        elif btn_id == "estoque":
            view_estoque.visible = True
            carregar_dados()
        elif btn_id == "caixa":
            view_vendas.visible = True
        
        page.update()

    # --- 8. Montagem do Layout ---
    sidebar = ft.Container(
        width=250, bgcolor=ft.Colors.BLUE_GREY_900, padding=20,
        content=ft.Column([
            ft.Text("PyPOS System", size=24, weight="bold", color=ft.Colors.WHITE),
            ft.Divider(color=ft.Colors.WHITE24),
            ft.Container(height=20),
            
            # FIX: Adicionado data="..." para identificação segura
            ft.TextButton("Dashboard", icon=ft.Icons.DASHBOARD, data="dashboard", on_click=navegar, style=ft.ButtonStyle(color=ft.Colors.WHITE)),
            ft.TextButton("Estoque", icon=ft.Icons.INVENTORY, data="estoque", on_click=navegar, style=ft.ButtonStyle(color=ft.Colors.BLUE_200)),
            ft.TextButton("Frente de Caixa", icon=ft.Icons.POINT_OF_SALE, data="caixa", on_click=navegar, style=ft.ButtonStyle(color=ft.Colors.WHITE)),
            
            ft.Container(expand=True), # Substituto do Spacer
            
            ft.TextButton("Sair", icon=ft.Icons.LOGOUT, icon_color=ft.Colors.RED_300, style=ft.ButtonStyle(color=ft.Colors.RED_200)),
        ])
    )

    conteudo = ft.Container(
        expand=True, padding=30,
        content=ft.Column([view_dashboard, view_estoque, view_vendas], expand=True)
    )

    page.add(ft.Row([sidebar, conteudo], expand=True, spacing=0))
    carregar_dados()

if __name__ == "__main__":
    ft.app(main)