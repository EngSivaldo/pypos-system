import flet as ft

class UsersPage(ft.Container):
    def __init__(self, page, auth_service):
        super().__init__()
        self.main_page = page
        self.auth_service = auth_service
        self.expand = True
        self.padding = 20
        self.bgcolor = "#f3f4f6"

        # Variável para controle de exclusão
        self.usuario_para_deletar = None

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

        self.btn_add = ft.ElevatedButton(
            "Cadastrar Usuário", 
            icon=ft.Icons.PERSON_ADD, 
            on_click=self._adicionar, 
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color="white")
        )

        # Lista de usuários
        self.lista_users = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

        # Modal de Confirmação de Exclusão
        self.dialog_confirm_user = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text("Tem certeza que deseja excluir este usuário?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self._fechar_confirm_user()),
                ft.ElevatedButton("Sim, Excluir", bgcolor="red", color="white", on_click=self._confirmar_exclusao_usuario)
            ]
        )

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
        # Adiciona o modal ao overlay da página quando ela carregar
        if self.page and self.dialog_confirm_user not in self.page.overlay:
            self.page.overlay.append(self.dialog_confirm_user)
        self.carregar_dados()

    def carregar_dados(self):
        self.lista_users.controls.clear()
        # Busca usuários através do auth_service
        users = self.auth_service.list_users()
        
        for u in users:
            # CORREÇÃO: O botão agora chama _preparar_deletar_usuario (Abre o Modal)
            btn_del = ft.IconButton(
                ft.Icons.DELETE, 
                icon_color=ft.Colors.RED, 
                data=u.id, 
                on_click=self._preparar_deletar_usuario 
            )
            
            # Impede deletar o admin principal
            if u.username == "admin": 
                btn_del.visible = False
            
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
            print(f"Erro ao adicionar: {ex}")

    def _preparar_deletar_usuario(self, e):
        """Abre o modal e guarda o ID do usuário selecionado"""
        self.usuario_para_deletar = e.control.data 
        self.dialog_confirm_user.open = True
        self.page.update()

    def _fechar_confirm_user(self):
        """Fecha o modal de confirmação"""
        self.dialog_confirm_user.open = False
        self.page.update()

    def _confirmar_exclusao_usuario(self, e):
        """Executa a exclusão real após o 'Sim' no modal"""
        try:
            # CORREÇÃO: Usando auth_service que foi passado no __init__
            self.auth_service.delete_user(self.usuario_para_deletar)
            self._fechar_confirm_user()
            self.carregar_dados() # Atualiza a lista na tela
            
            snack = ft.SnackBar(ft.Text("Usuário excluído com sucesso!"), bgcolor="blue")
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()
        except Exception as ex:
            print(f"Erro ao excluir: {ex}")
            self._fechar_confirm_user()