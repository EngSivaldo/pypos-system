Este documento serve tanto para você (desenvolvedor) consultar no futuro, quanto para entregar a outro programador que venha a trabalhar no projeto.

📘 Manual Técnico e Operacional: PyPOS Enterprise
Versão: 1.1 (Arquitetura Blindada) Data: 02/01/2026

1. Visão Geral das Mudanças
   O sistema passou por uma reestruturação de Entrypoint (Ponto de Entrada) e recebeu camadas de Segurança de Dados. O objetivo foi separar a responsabilidade de "Infraestrutura" da responsabilidade de "Interface Visual", garantindo que backups e logs ocorram antes mesmo da janela abrir.

1.1 Nova Estrutura de Pastas
A execução do projeto agora é centralizada na raiz da pasta src.

Plaintext

pypos_system/
├── src/
│ ├── main.py <-- [NOVO] O Gerente (Inicia tudo)
│ ├── utils.py <-- [NOVO] Ferramentas (Backup/Log)
│ ├── config/
│ │ └── settings.py
│ └── views/
│ ├── login_view.py <-- Interface de Login (Continua aqui)
│ └── ...
├── backups/ <-- [AUTO] Pasta criada automaticamente
└── sistema_erros.log <-- [AUTO] Arquivo de registro de falhas 2. Arquitetura de Inicialização (src/main.py)
O arquivo src/views/main_view.py foi descontinuado como inicializador. O novo responsável é o src/main.py.

O Fluxo de Execução:
Correção de Contexto: O script ajusta o sys.path para garantir que o Python enxergue a raiz do projeto, resolvendo erros de importação (ModuleNotFoundError).

Protocolos de Segurança: Antes de carregar qualquer interface gráfica:

Inicia o sistema de Logs.

Executa o Backup Automático.

Conexão com Banco: Cria a engine do SQLAlchemy e ativa a proteção WAL.

Interface Gráfica: Só após tudo isso, o Flet é iniciado e a tela de Login é exibida.

3. Tecnologias de Proteção de Dados
   Implementamos duas camadas de defesa para evitar perda de dados em quedas de energia ou falhas de hardware.

3.1 Modo WAL (Write-Ahead Logging)
O SQLite foi configurado para operar em modo WAL.

Como funciona: Em vez de escrever diretamente no arquivo .db (o que é arriscado se a luz acabar no meio da escrita), o sistema grava as mudanças em um arquivo temporário .wal. O sistema consolida esses dados periodicamente de forma segura.

Benefício: Reduz drasticamente a chance de corromper o banco ("Database Malformed") e melhora a velocidade do sistema.

Implementação: Via event.listen no SQLAlchemy dentro do main.py.

3.2 Sistema de Logs (utils.py)
O sistema agora possui uma "Caixa Preta".

Arquivo: sistema_erros.log (na raiz).

O que grava: Erros críticos de execução, falhas de backup e erros de impressão.

Uso: Se o cliente relatar um erro, abra este arquivo para ver a data, hora e o motivo técnico da falha.

4. Política de Backup Automático
   O sistema possui uma rotina de preservação de dados "Zero-Click" (sem intervenção do usuário).

Como Funciona
Gatilho: Executado automaticamente toda vez que o sistema é aberto (boot).

Local: Pasta backups/ na raiz do projeto.

Formato: pypos_backup_AAAA-MM-DD.db (Ex: pypos_backup_2026-01-02.db).

Regra de Retenção: Um arquivo por dia. Se o sistema for aberto 10 vezes no mesmo dia, o arquivo do dia será atualizado para a versão mais recente.

🆘 Procedimento de Restauração (Disaster Recovery)
Caso o banco de dados principal (pypos.db) seja corrompido ou deletado:

Feche o sistema PyPOS.

Vá até a pasta do projeto.

Delete ou renomeie o arquivo pypos.db (o danificado).

Abra a pasta backups.

Copie o arquivo com a data mais recente.

Cole na raiz do projeto.

Renomeie o arquivo copiado para pypos.db.

Abra o sistema. Tudo estará restaurado até o último acesso.

5. Guia do Desenvolvedor (Como Rodar)
   Devido à reestruturação, o comando para rodar o projeto em desenvolvimento mudou.

❌ Comando Antigo (Não usar): python -m src.views.main_view

✅ Novo Comando Oficial:

PowerShell

python src/main.py
Notas Importantes:
Se precisar limpar o banco de dados para testes, basta deletar o arquivo pypos.db. Um novo será criado automaticamente (vazio) na próxima execução.

O arquivo src/views/main_view.py pode ser excluído, pois sua lógica foi migrada para o main.py.
