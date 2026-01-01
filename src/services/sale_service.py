from sqlalchemy.orm import Session
from src.models.sale import Sale, SaleItem
from src.models.product import Product
from decimal import Decimal

class SaleService:
    def __init__(self, session: Session):
        self.session = session

    def create_sale(self, items_data: list):
        """
        Recebe uma lista: [{'barcode': '123', 'quantity': 2}, ...]
        """
        if not items_data:
            raise ValueError("A venda não pode estar vazia.")

        # 1. Cria a Venda
        # NÃO passamos ID (gerado auto) nem total (padrão 0)
        new_sale = Sale() 
        
        total = Decimal("0.0")
        
        # 2. Processa os itens
        for item in items_data:
            barcode = item['barcode']
            qtd = item['quantity']

            # Busca o produto
            product = self.session.query(Product).filter(Product.barcode == barcode).first()
            if not product:
                raise ValueError(f"Produto {barcode} não encontrado no banco.")
            
            if product.stock_quantity < qtd:
                raise ValueError(f"Estoque insuficiente para {product.name}.")

            # Baixa no Estoque
            product.stock_quantity -= qtd
            
            # Calcula preço (Garante Decimal)
            price = Decimal(str(product.price))
            subtotal = price * Decimal(str(qtd))
            total += subtotal

            # 3. Cria o Item
            # NOTA: Não passamos sale_id aqui. O relacionamento resolve depois.
            sale_item = SaleItem(
                product_id=product.id,
                quantity=qtd,
                unit_price=price
            )
            
            # A MÁGICA DO ORM: Adicionamos o item à lista da venda.
            # O SQLAlchemy vai pegar o ID da venda e colocar no sale_item automaticamente.
            new_sale.items.append(sale_item)

        # 4. Atualiza o total
        new_sale.total_amount = total

        # 5. Salva tudo
        try:
            self.session.add(new_sale)
            self.session.commit()
            return new_sale
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Erro ao salvar venda: {str(e)}")
        


    def get_dashboard_stats(self):
        from sqlalchemy import func
        from datetime import date
        
        # 1. Total de Vendas (Geral)
        total_sales = self.session.query(func.sum(Sale.total_amount)).scalar() or 0
        
        # 2. Vendas de Hoje
        today = date.today()
        # Filtro simples: pega tudo que for maior ou igual a meia-noite de hoje
        sales_today = self.session.query(func.sum(Sale.total_amount))\
            .filter(func.date(Sale.created_at) == today).scalar() or 0
            
        # 3. Contagem de Vendas
        count_sales = self.session.query(func.count(Sale.id)).scalar() or 0
        
        # 4. Ticket Médio
        avg_ticket = total_sales / count_sales if count_sales > 0 else 0
        
        return {
            "total_geral": Decimal(str(total_sales)),
            "vendas_hoje": Decimal(str(sales_today)),
            "ticket_medio": Decimal(str(avg_ticket))
        }
        
        
    def list_sales(self):
        """Lista todas as vendas ordenadas por data (mais recente primeiro)"""
        # O sale.items e sale.items.product serão carregados automaticamente pelo SQLAlchemy
        return self.session.query(Sale).order_by(Sale.created_at.desc()).all()