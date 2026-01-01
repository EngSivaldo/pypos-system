import flet as ft

class SettingsPage(ft.Container):
    def __init__(self, page, settings_service):
        super().__init__()
        self.main_page = page
        self.settings_service = settings_service
        self.expand = True
        self.padding = 30
        self.bgcolor = "#f3f4f6"

        # Campos
        self.txt_empresa = ft.TextField(label="Nome da Empresa", border_radius=8)
        self.txt_cnpj = ft.TextField(label="CNPJ / CPF", border_radius=8)
        self.txt_endereco = ft.TextField(label="Endereço", border_radius=8)
        self.txt_rodape = ft.TextField(label="Mensagem do Rodapé (Cupom)", border_radius=8)

        self.content = ft.Column([
            ft.Text("Configurações da Loja", size=28, weight="bold", color=ft.Colors.BLUE_GREY_900),
            ft.Text("Personalize os dados que saem no cupom fiscal.", size=14, color=ft.Colors.GREY_600),
            ft.Divider(color="transparent", height=20),
            
            ft.Container(
                content=ft.Column([
                    self.txt_empresa,
                    self.txt_cnpj,
                    self.txt_endereco,
                    self.txt_rodape,
                    ft.Divider(),
                    ft.ElevatedButton(
                        "Salvar Configurações",
                        icon=ft.Icons.SAVE,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, padding=20),
                        on_click=self._salvar
                    )
                ]),
                bgcolor=ft.Colors.WHITE, padding=30, border_radius=10, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12), width=600
            )
        ], expand=True)

    def did_mount(self):
        # Carrega dados ao entrar na tela
        cfg = self.settings_service.get_settings()
        self.txt_empresa.value = cfg.company_name
        self.txt_cnpj.value = cfg.cnpj
        self.txt_endereco.value = cfg.address
        self.txt_rodape.value = cfg.receipt_footer
        self.update()

    def _salvar(self, e):
        try:
            self.settings_service.save_settings(
                self.txt_empresa.value,
                self.txt_cnpj.value,
                self.txt_endereco.value,
                self.txt_rodape.value
            )
            
            snack = ft.SnackBar(ft.Text("Configurações Salvas!"), bgcolor="green")
            self.main_page.overlay.append(snack)
            snack.open = True
            self.main_page.update()
        except Exception as ex:
            print(f"Erro: {ex}")