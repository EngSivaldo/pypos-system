import flet as ft

class UsersPage(ft.Container):
    def __init__(self, page, auth_service):
        super().__init__()
        self.main_page = page
        self.auth_service = auth_service
        self.expand = True
        self.padding = 20
        self.bgcolor = "#f3f4f6"

        # Formulário
        self.txt_nome = ft.TextField(label="Nome Completo", expand=True)
        self.txt_user = ft.TextField(label="Usuário (Login)", expand=True)
        self.txt_pass = ft.TextField(label="Senha Inicial", password=True, can_reveal_password=True, expand=True)
        self.dd_role = ft.Dropdown(
            label="Cargo",
            options=[
                ft.dropdown.Option("operator", "Operador de Caixa"),
                ft.dropdown.Option("admin", "Administrador"),
            ],
            value="operator",
            width=200
        )

        self.btn_add = ft.ElevatedButton("Cadastrar Usuário", icon=ft.Icons.PERSON_ADD, on_click=self._adicionar, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color="white"))

        # Lista
        self.lista_users = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

        self.content = ft.Column([
            ft.Text("Gestão de Usuários", size=28, weight="bold", color=ft.Colors.BLUE_GREY_900),
            ft.Divider(),
            
            # Card de Cadastro
            ft.Container(
                content=ft.Column([
                    ft.Text("Novo Cadastro", weight="bold"),
                    ft.Row([self.txt_nome, self.txt_user, self.txt_pass]),
                    ft.Row([self.dd_role, self.btn_add])
                ]),
                bgcolor="white", padding=20, border_radius=10, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)
            ),
            
            ft.Divider(height=30, color="transparent"),
            ft.Text("Equipe Cadastrada", size=20, weight="bold"),
            self.lista_users
        ], expand=True)

    def did_mount(self):
        self.carregar_dados()

    def carregar_dados(self):
        self.lista_users.controls.clear()
        users = self.auth_service.list_users()
        
        for u in users:
            # Não permite deletar o admin principal
            btn_del = ft.IconButton(ft.Icons.DELETE, ft.Colors.RED, data=u.id, on_click=self._remover)
            if u.username == "admin": btn_del.visible = False
            
            card = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SUPERVISOR_ACCOUNT if u.role == 'admin' else ft.Icons.PERSON),
                    ft.Column([
                        ft.Text(u.name, weight="bold"),
                        ft.Text(f"@{u.username} - {u.role.upper()}", size=12, color="grey")
                    ], expand=True),
                    btn_del
                ]),
                bgcolor="white", padding=10, border_radius=8, border=ft.border.all(1, "#e5e7eb")
            )
            self.lista_users.controls.append(card)
        self.update()

    def _adicionar(self, e):
        try:
            if not self.txt_nome.value or not self.txt_user.value or not self.txt_pass.value:
                return
            
            self.auth_service.create_user(
                self.txt_nome.value, 
                self.txt_user.value, 
                self.txt_pass.value, 
                self.dd_role.value
            )
            
            self.txt_nome.value = ""
            self.txt_user.value = ""
            self.txt_pass.value = ""
            self.carregar_dados()
            
            snack = ft.SnackBar(ft.Text("Usuário cadastrado!"), bgcolor="green")
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()
            
        except Exception as ex:
            print(ex)

    def _remover(self, e):
        self.auth_service.delete_user(e.control.data)
        self.carregar_dados()
        
        
  #Será a tela onde o Admin cadastra a equipe.