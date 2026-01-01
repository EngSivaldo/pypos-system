import flet as ft
import time

class LoginView(ft.Container):
    def __init__(self, page, auth_service, on_login_success):
        super().__init__()
        self.main_page = page 
        self.auth_service = auth_service
        self.on_login_success = on_login_success 
        
        self.expand = True
        self.bgcolor = "#111827"
        
        # CORREÇÃO AQUI: Trocamos ft.alignment.center por ft.Alignment(0,0)
        self.alignment = ft.Alignment(0, 0)

        # Campos
        self.txt_user = ft.TextField(
            label="Usuário", 
            prefix_icon=ft.Icons.PERSON, 
            border_radius=8, 
            bgcolor=ft.Colors.WHITE, 
            color=ft.Colors.BLACK
        )
        self.txt_pass = ft.TextField(
            label="Senha", 
            prefix_icon=ft.Icons.LOCK, 
            password=True, 
            can_reveal_password=True, 
            border_radius=8, 
            bgcolor=ft.Colors.WHITE, 
            color=ft.Colors.BLACK,
            on_submit=self._fazer_login
        )
        
        self.btn_entrar = ft.ElevatedButton(
            "ENTRAR NO SISTEMA",
            icon=ft.Icons.LOGIN,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600, 
                color=ft.Colors.WHITE, 
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            width=300,
            on_click=self._fazer_login
        )
        
        self.error_text = ft.Text("", color=ft.Colors.RED_400, size=14, weight="bold")

        # Card de Login
        self.content = ft.Container(
            width=400,
            padding=40,
            bgcolor=ft.Colors.WHITE10,
            border_radius=15,
            border=ft.border.all(1, ft.Colors.WHITE24),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK),
            content=ft.Column([
                ft.Icon(ft.Icons.ROCKET_LAUNCH, size=60, color=ft.Colors.BLUE_400),
                ft.Text("PyPOS Enterprise", size=24, weight="bold", color=ft.Colors.WHITE),
                ft.Text("Acesso Restrito", size=12, color=ft.Colors.GREY_400),
                ft.Divider(color="transparent", height=20),
                self.txt_user,
                self.txt_pass,
                self.error_text,
                ft.Divider(color="transparent", height=10),
                self.btn_entrar
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def _fazer_login(self, e):
        self.error_text.value = ""
        self.btn_entrar.disabled = True
        self.update()
        
        time.sleep(0.5)
        
        user = self.auth_service.login(self.txt_user.value, self.txt_pass.value)
        
        if user:
            self.on_login_success(user)
        else:
            self.error_text.value = "Usuário ou senha incorretos."
            self.btn_entrar.disabled = False
            self.update()