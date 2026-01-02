# Arquivo: utils.py
import shutil
import os
import logging
from datetime import datetime

# --- CONFIGURAÇÃO DE LOGS (CAIXA PRETA) ---
def configurar_logs():
    # Cria o arquivo de log se não existir e define o formato
    logging.basicConfig(
        filename='sistema_erros.log', 
        level=logging.ERROR, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )
    logging.info("Sistema de logs iniciado.")

# --- SISTEMA DE BACKUP AUTOMÁTICO ---
def realizar_backup_banco():
    arquivo_banco = "pypos.db"
    pasta_backup = "backups"

    # Só faz backup se o banco existir
    if os.path.exists(arquivo_banco):
        try:
            # Cria a pasta 'backups' se ela não existir
            if not os.path.exists(pasta_backup):
                os.makedirs(pasta_backup)
            
            # Define o nome do arquivo: ex: backup_2023-10-25.db
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            destino = os.path.join(pasta_backup, f"pypos_backup_{data_hoje}.db")
            
            # Copia o arquivo
            shutil.copy(arquivo_banco, destino)
            print(f"✅ Backup realizado com sucesso: {destino}")
        except Exception as e:
            # Se der erro no backup, grava no log, mas não trava o sistema
            logging.error(f"Falha ao criar backup: {e}")
            print(f"❌ Erro no backup: {e}")
    else:
        print("⚠️ Banco de dados ainda não existe (primeira execução).")