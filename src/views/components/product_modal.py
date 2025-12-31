import flet as ft

class ProductModal:
    def __init__(self, page, on_save_callback):
        self.main_page = page 
        self.on_save = on_save_callback
        self.product_id = None 
        
        # --- Campos Estilizados (Compatível com sua versão) ---
        self.txt_nome = ft.TextField(
            label="Nome do Produto", 
            prefix_icon=ft.Icons.SHOPPING_BAG_OUTLINED,
            border_radius=10
        )
        self.txt_codigo = ft.TextField(
            label="Código de Barras", 
            prefix_icon=ft.Icons.QR_CODE,
            border_radius=10
        )
        # CORREÇÃO: Usando 'prefix' com ft.Text em vez de 'prefix_text'
        self.txt_preco = ft.TextField(
            label="Preço", 
            keyboard_type=ft.KeyboardType.NUMBER, 
            prefix=ft.Text("R$ "), 
            border_radius=10,
            expand=True
        )
        self.txt_estoque = ft.TextField(
            label="Estoque", 
            value="0", 
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.INVENTORY_2_OUTLINED,
            border_radius=10,
            expand=True
        )

        # --- Layout do Conteúdo ---
        form_content = ft.Column([
            ft.Text("Dados do Produto", weight="bold", size=16),
            self.txt_nome,
            self.txt_codigo,
            ft.Row([self.txt_preco, self.txt_estoque], spacing=10),
        ], tight=True, width=450)

        # --- Dialog ---
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Gerenciar Produto", weight="bold"),
            content=form_content,
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar, style=ft.ButtonStyle(color=ft.Colors.GREY_600)),
                ft.ElevatedButton("Salvar Produto", icon=ft.Icons.SAVE, on_click=self._salvar_click, 
                                  style=ft.ButtonStyle(
                                      bgcolor=ft.Colors.BLUE_600, 
                                      color=ft.Colors.WHITE,
                                      padding=15,
                                      shape=ft.RoundedRectangleBorder(radius=8)
                                  )),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        
        # Modo Overlay (Obrigatório para funcionar no seu ambiente)
        self.main_page.overlay.append(self.dialog)

    def abrir(self, produto=None):
        self.product_id = None
        
        if produto:
            self.product_id = produto.id
            self.dialog.title.value = "Editar Produto"
            self.txt_nome.value = produto.name
            self.txt_codigo.value = produto.barcode
            self.txt_codigo.disabled = True
            self.txt_preco.value = f"{produto.price:.2f}"
            self.txt_estoque.value = str(produto.stock_quantity)
        else:
            self.dialog.title.value = "Novo Produto"
            self.txt_nome.value = ""
            self.txt_codigo.value = ""
            self.txt_codigo.disabled = False
            self.txt_preco.value = ""
            self.txt_estoque.value = "0"
            
        self.dialog.open = True
        self.main_page.update()

    def fechar(self, e=None):
        self.dialog.open = False
        self.main_page.update()

    def _salvar_click(self, e):
        dados = {
            "id": self.product_id,
            "name": self.txt_nome.value,
            "barcode": self.txt_codigo.value,
            "price": self.txt_preco.value.replace(",", "."),
            "stock": self.txt_estoque.value
        }
        self.on_save(dados)
        self.fechar()