import unittest
import sys
import os

# Ajusta o caminho para encontrar a pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
from src.models.product import Product
from src.models.sale import Sale, SaleItem

class TestModels(unittest.TestCase):

    def setUp(self):
        # Cria banco na memória
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_criar_produto(self):
        """Teste: Deve criar um produto e recuperar seus dados corretamente"""
        print("\n🧪 Testando Criação de Produto...")
        
        novo_prod = Product(
            name="Coca Cola 2L",
            price=10.50,
            stock_quantity=100, 
            barcode="789123456" 
        )
        self.session.add(novo_prod)
        self.session.commit()

        produto_salvo = self.session.query(Product).filter_by(barcode="789123456").first()
        
        self.assertIsNotNone(produto_salvo)
        self.assertEqual(produto_salvo.name, "Coca Cola 2L")
        self.assertEqual(float(produto_salvo.price), 10.50)
        self.assertEqual(produto_salvo.stock_quantity, 100)
        print("✅ Produto criado e verificado com sucesso!")

    def test_criar_venda_com_itens(self):
        """Teste: Deve criar uma Venda vinculada a Itens e Produtos"""
        print("\n🧪 Testando Relacionamento Venda <-> Itens...")

        prod = Product(
            name="Biscoito", 
            price=5.00, 
            stock_quantity=50, 
            barcode="BISCOITO123"
        )
        self.session.add(prod)
        self.session.commit()

        # Venda vazia primeiro (pois total_amount é init=False)
        venda = Sale()
        venda.total_amount = 10.00
        self.session.add(venda)
        self.session.commit()

        # --- CORREÇÃO FINAL AQUI ---
        # 1. Criamos o item SEM passar o sale_id (pois é init=False)
        item = SaleItem(
            product_id=prod.id,
            quantity=2,
            unit_price=5.00
        )
        # 2. Atribuímos a venda manualmente DEPOIS de criar
        item.sale_id = venda.id
        
        self.session.add(item)
        self.session.commit()

        venda_recuperada = self.session.query(Sale).filter_by(id=venda.id).first()
        
        self.assertEqual(len(venda_recuperada.items), 1)
        self.assertEqual(venda_recuperada.items[0].product.name, "Biscoito")
        print("✅ Venda e Itens relacionados com sucesso!")

if __name__ == '__main__':
    unittest.main()