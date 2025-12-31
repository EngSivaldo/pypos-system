# Regras de Negócio da Venda.
#sale_service.py (O Caixa): Vai cuidar da lógica da Venda. Ele será usado quando formos processar o carrinho de compras, calcular troco e fechar a nota fiscal.
# Ex: Calcular totais, validar estoque antes de chamar o repository.

from datetime import datetime
from sqlalchemy.orm import Session
from src.models.product import Product
from src.models.sale import Sale, SaleItem

class SaleService:
    def __init__(self, session: Session):
        self.session = session

    def create_sale(self, items: list[dict]) -> Sale:
        """
        Registra uma nova venda e abate o estoque.
        
        :param items: Lista de dicionários [{'barcode': '123', 'quantity': 2}, ...]
        """
        # 1. Inicia a Venda (Cabeçalho)
        new_sale = Sale(total_amount=0.0)
        
        total = 0.0
        
        # 2. Processa cada item do carrinho
        for item_data in items:
            barcode = item_data['barcode']
            qtd_vendida = item_data['quantity']

            # Busca o produto
            product = self.session.query(Product).filter_by(barcode=barcode).first()
            
            if not product:
                raise ValueError(f"Produto não encontrado: {barcode}")
            
            if product.stock_quantity < qtd_vendida:
                raise ValueError(f"Estoque insuficiente para '{product.name}'. Restam apenas {product.stock_quantity}.")

            # 3. Abate o Estoque (Regra de Ouro)
            product.stock_quantity -= qtd_vendida
            
            # 4. Cria o item da venda
            sale_item = SaleItem(
                product_id=product.id,
                quantity=qtd_vendida,
                unit_price=product.price,
                sale=new_sale # Linka com a venda pai
            )
            
            # Calcula subtotal
            total += (float(product.price) * qtd_vendida)
            
            # Adiciona na sessão
            self.session.add(sale_item)

        # 5. Finaliza
        new_sale.total_amount = total
        new_sale.created_at = datetime.now()
        
        self.session.add(new_sale)
        self.session.commit()
        self.session.refresh(new_sale)
        
        return new_sale