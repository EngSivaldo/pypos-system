from sqlalchemy.orm import Session
from src.models.sale import Sale, SaleItem
from src.models.product import Product
from decimal import Decimal
from sqlalchemy import func
from datetime import date

class SaleService:
    def __init__(self, session: Session):
        self.session = session

    def create_sale(self, items_data: list, user_id: int = 1):
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
        """Retorna estatísticas para o Dashboard, incluindo o Ranking de Produtos"""
        
        # 1. Total de Vendas (Geral)
        total_sales = self.session.query(func.sum(Sale.total_amount)).scalar() or 0
        
        # 2. Vendas de Hoje
        today = date.today()
        sales_today = self.session.query(func.sum(Sale.total_amount))\
            .filter(func.date(Sale.created_at) == today).scalar() or 0
            
        # 3. Contagem de Vendas
        count_sales = self.session.query(func.count(Sale.id)).scalar() or 0
        
        # 4. Ticket Médio
        avg_ticket = total_sales / count_sales if count_sales > 0 else 0

        # --- NOVO: RANKING DE PRODUTOS MAIS VENDIDOS ---
        # Busca o nome do produto e a soma das quantidades vendidas
        top_products_query = self.session.query(
            Product.name,
            func.sum(SaleItem.quantity).label('total_qtd')
        ).join(SaleItem, Product.id == SaleItem.product_id)\
         .group_by(Product.name)\
         .order_by(func.sum(SaleItem.quantity).desc())\
         .limit(5).all()

        # Converte o resultado da query para uma lista de (nome, quantidade)
        top_produtos_list = [(item.name, int(item.total_qtd)) for item in top_products_query]
        
        return {
            "total_geral": Decimal(str(total_sales)),
            "vendas_hoje": Decimal(str(sales_today)),
            "ticket_medio": Decimal(str(avg_ticket)),
            "top_produtos": top_produtos_list  # Chave usada pela DashboardPage
        }
        
    def list_sales(self):
        """Lista todas as vendas ordenadas por data (mais recente primeiro)"""
        return self.session.query(Sale).order_by(Sale.created_at.desc()).all()

    def get_daily_closure(self, target_date: date = None):
        """
        FUNÇÃO DE FECHAMENTO DE CAIXA:
        Soma todas as vendas de uma data específica (padrão hoje).
        """
        if target_date is None:
            target_date = date.today()

        summary = self.session.query(
            func.count(Sale.id).label('total_vendas'),
            func.sum(Sale.total_amount).label('faturamento')
        ).filter(func.date(Sale.created_at) == target_date).first()

        return {
            "data": target_date.strftime('%d/%m/%Y'),
            "quantidade_vendas": summary.total_vendas or 0,
            "faturamento_total": Decimal(str(summary.faturamento or 0))
        }