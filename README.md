# PyPOS - Sistema PDV (Point of Sale)

Sistema de Ponto de Venda Desktop desenvolvido em Python com foco em Arquitetura Limpa (Clean Architecture), escalabilidade e interface moderna.

## 🚀 Tech Stack

- **Linguagem:** Python 3.10+
- **Interface (GUI):** Flet (Flutter wrapper)
- **Banco de Dados:** SQLite (Dev) / PostgreSQL (Prod)
- **ORM:** SQLAlchemy 2.0
- **Migrações:** Alembic
- **Validação:** Pydantic

## 🏗 Arquitetura

O projeto segue uma adaptação de Clean Architecture modularizada:

- `src/models`: Definição de tabelas e entidades (SQLAlchemy).
- `src/repositories`: Padrão Repository para abstração de acesso a dados.
- `src/services`: Regras de negócio, validações e transações.
- `src/views`: Interface Gráfica (separada da lógica).

## ⚙️ Configuração do Ambiente

1.  **Clone o repositório:**

    ```bash
    git clone [https://github.com/SEU_USUARIO/pypos.git](https://github.com/SEU_USUARIO/pypos.git)
    cd pypos
    ```

2.  **Crie o ambiente virtual:**

    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicialize o Banco de Dados:**

    ```bash
    alembic upgrade head
    ```

5.  **Execute a aplicação:**
    ```bash
    python -m src.views.main_view
    ```

## 📝 Status do Projeto

- [x] Estrutura de Diretórios (Scaffolding)
- [x] Configuração de Banco de Dados e Migrações (Alembic)
- [x] CRUD de Produtos (Backend & Repository)
- [ ] Interface de Cadastro de Produtos
- [ ] Frente de Caixa (Venda)
- [ ] Geração de Comprovantes
