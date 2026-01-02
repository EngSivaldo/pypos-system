🛠️ Protocolo de Instalação: PyPOS Enterprise
Destinatário: Equipe Técnica Objetivo: Instalação limpa e funcional no ambiente do cliente.

📍 Passo 1: Transferência Segura (Não pule este passo)
Nunca execute os instaladores direto do Pen Drive. O Windows costuma bloquear arquivos que rodam direto de mídias removíveis.

Conecte o Pen Drive no computador do cliente.

Copie a pasta inteira Instalacao_PyPOS para a Área de Trabalho (Desktop) do cliente.

Remova o Pen Drive.

Abra a pasta que você acabou de copiar na Área de Trabalho.

⚙️ Passo 2: Preparando o Terreno (Dependências)
Antes de instalar o sistema, precisamos garantir que o Windows tem as peças necessárias para rodar Python.

Execute o arquivo VC_redist.x64.exe.

Cenário A: Se aparecer a opção "Instalar", clique nela e aguarde finalizar.

Cenário B: Se aparecer "Reparar" ou "Desinstalar", significa que o cliente já tem isso instalado. Pode fechar/cancelar.

Nota: Se pedir para reiniciar, reinicie o computador agora.

🚀 Passo 3: Instalando o PyPOS Enterprise
Agora vamos instalar o sistema principal.

Clique com o botão direito no arquivo Instalador_PyPOS_v1.exe.

Selecione a opção "Executar como administrador" (Isso garante que o sistema possa criar a pasta de banco de dados e backups sem erro).

⚠️ Alerta do Windows (Tela Azul - SmartScreen):

Provavelmente o Windows vai dizer: "O Windows protegeu o computador".

Clique no texto pequeno "Mais informações".

Clique no botão "Executar assim mesmo".

Siga o assistente: Avançar > Aceitar > Instalar.

Na tela final, deixe marcada a opção "Iniciar PyPOS Enterprise" e clique em Concluir.

🛡️ Passo 4: Configurando Antivírus (Se necessário)
Se o sistema não abrir ou se o antivírus (Avast, McAfee, Norton) der algum alerta:

Abra o Antivírus do cliente.

Procure por "Exceções" ou "Lista de Confiáveis".

Adicione a pasta de instalação inteira:

Caminho padrão: C:\Arquivos de Programas (x86)\PyPOS_Enterprise (ou similar).

Isso impede que o antivírus apague o seu .exe numa varredura futura.

✅ Passo 5: Validação Final (O Teste dos 3 Pontos)
Não saia do cliente sem fazer estes 3 testes:

Teste de Abertura:

Feche o sistema (se estiver aberto).

Abra novamente pelo ícone da Área de Trabalho.

Faça login (admin / admin123).

Teste de Banco de Dados:

Vá em Estoque > Adicione um produto teste (Ex: "Teste 01").

Clique em Salvar.

Feche o sistema e abra de novo. O "Teste 01" ainda está lá? (Se sim, o banco está gravando).

Teste de Backup (A Prova Real):

Clique com o botão direito no ícone do PyPOS na Área de Trabalho.

Escolha "Abrir local do arquivo".

Procure pela pasta backups.

Entre nela e veja se existe um arquivo com a data de hoje (Ex: pypos_backup_2026-01-02.db).

🤝 Passo 6: Finalização
Instale (ou apenas copie) o AnyDesk para a Área de Trabalho, caso precise dar suporte remoto.

Deixe o arquivo Manual_Usuario.pdf na Área de Trabalho para o cliente consultar.

Apague a pasta de instalação (Instalacao_PyPOS) que você copiou para o Desktop (para não deixar "lixo" no PC do cliente).
