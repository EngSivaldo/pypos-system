import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.base import Base
from src.models.product import Product
from src.services.product_service import ProductService

class TestProductService(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.service = ProductService(self.session)

    def tearDown(self):
        self.session.close()

    def test_listar_produtos(self):
        """Teste: O service deve retornar a lista de produtos cadastrados"""
        print("\n🧪 Testando Service de Listagem...")
        
        # CORREÇÃO: Adicionado 'barcode' nos dois produtos
        p1 = Product(
            name="Prod A", 
            price=10, 
            stock_quantity=10, 
            barcode="AAA111" # <--- OBRIGATÓRIO
        )
        p2 = Product(
            name="Prod B", 
            price=20, 
            stock_quantity=20, 
            barcode="BBB222" # <--- OBRIGATÓRIO
        )
        self.session.add_all([p1, p2])
        self.session.commit()

        # Tenta listar
        try:
            lista = self.service.list_products()
        except AttributeError:
            lista = self.service.get_all_products()
        
        self.assertEqual(len(lista), 2)
        print("✅ Service listou corretamente 2 produtos.")

if __name__ == '__main__':
    unittest.main()