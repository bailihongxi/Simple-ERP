import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service
from database.db import execute


class TestSalesZeroStockRed(unittest.TestCase):
    """测试销售模块商品下拉库存为0标红（问题8）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM products WHERE name LIKE '问题8_%'")
        # 创建一个有库存的商品和一个无库存的商品
        cls.product_in_stock = product_service.create_product({
            'name': '问题8_有库存商品', 'purchase_price': '5', 'sale_price': '20'
        })
        cls.product_zero_stock = product_service.create_product({
            'name': '问题8_无库存商品', 'purchase_price': '5', 'sale_price': '20'
        })
        # 给有库存商品设置库存
        execute("UPDATE products SET current_stock = 50 WHERE id = ?", (cls.product_in_stock,))
        execute("UPDATE products SET current_stock = 0 WHERE id = ?", (cls.product_zero_stock,))

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '问题8_%'")

    def test_sales_page_renders(self):
        """测试销售页面正常渲染"""
        resp = self.client.get('/sales/')
        self.assertEqual(resp.status_code, 200)

    def test_sales_page_products_include_stock(self):
        """测试销售页面的products数据包含current_stock字段"""
        resp = self.client.get('/sales/')
        html = resp.get_data(as_text=True)
        # 页面中应该有products的JSON数据，包含current_stock
        self.assertIn('current_stock', html)

    def test_sales_page_has_zero_stock_red_logic(self):
        """测试销售页面包含库存为0标红的JS逻辑"""
        resp = self.client.get('/sales/')
        html = resp.get_data(as_text=True)
        # 检查JS代码中包含库存判断和红色样式
        self.assertIn('stock <= 0', html)
        self.assertIn('color:#dc3545', html)
        self.assertIn('无货', html)

    def test_zero_stock_product_in_page_data(self):
        """测试无库存商品出现在页面数据中"""
        resp = self.client.get('/sales/')
        html = resp.get_data(as_text=True)
        # 页面中products是JSON，中文可能被转义为unicode，检查商品ID
        self.assertIn(f'"id": {self.product_zero_stock}', html)
        # 检查该商品库存为0
        import json, re
        match = re.search(r'var products = (\[.*?\]);', html, re.DOTALL)
        self.assertIsNotNone(match)
        products = json.loads(match.group(1))
        zero_product = next((p for p in products if p['id'] == self.product_zero_stock), None)
        self.assertIsNotNone(zero_product)
        self.assertEqual(zero_product['current_stock'], 0)

    def test_create_sale_zero_stock_blocked(self):
        """测试库存为0的商品无法创建销售"""
        from services import sales_service
        with self.assertRaises(ValueError) as ctx:
            sales_service.create_sale({
                'sale_date': '2026-08-12',
                'product_id': self.product_zero_stock,
                'quantity': '1',
                'unit_price': '20',
                'payment_type': 'cash',
                'notes': '问题8_测试'
            })
        self.assertIn('库存不足', str(ctx.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
