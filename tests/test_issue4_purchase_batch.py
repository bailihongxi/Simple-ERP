import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service, supplier_service, purchase_service
from database.db import execute


class TestPurchaseBatchDelete(unittest.TestCase):
    """测试采购批量删除功能（问题4）"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM purchases WHERE notes LIKE '问题4_%'")
        execute("DELETE FROM products WHERE name LIKE '问题4_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题4_%'")
        cls.product_id = product_service.create_product({
            'name': '问题4_批量商品', 'purchase_price': '10', 'sale_price': '20'
        })
        cls.supplier_id = supplier_service.create_supplier({
            'name': '问题4_批量供应商'
        })

    def setUp(self):
        # 每个测试前清理该商品的所有采购记录，重置库存和avg_cost
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM purchases WHERE notes LIKE '问题4_%'")
        execute("DELETE FROM products WHERE name LIKE '问题4_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题4_%'")

    def test_batch_delete_multiple_records(self):
        """测试批量删除多条采购记录"""
        # 创建3条采购记录，库存增加30
        p1 = purchase_service.create_purchase({
            'purchase_date': '2026-08-12', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '5', 'unit_price': '10',
            'payment_type': 'cash', 'notes': '问题4_批量1'
        })
        p2 = purchase_service.create_purchase({
            'purchase_date': '2026-08-12', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '12',
            'payment_type': 'cash', 'notes': '问题4_批量2'
        })
        p3 = purchase_service.create_purchase({
            'purchase_date': '2026-08-12', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '15', 'unit_price': '8',
            'payment_type': 'cash', 'notes': '问题4_批量3'
        })

        product = product_service.get_product_by_id(self.product_id)
        stock_before = product['current_stock']

        # 批量删除前2条
        count = purchase_service.batch_delete_purchases([p1, p2])
        self.assertEqual(count, 2)

        # 验证库存回退了15（5+10）
        product = product_service.get_product_by_id(self.product_id)
        self.assertEqual(product['current_stock'], stock_before - 15)

        # 验证记录已删除
        self.assertIsNone(purchase_service.get_purchase_by_id(p1))
        self.assertIsNone(purchase_service.get_purchase_by_id(p2))
        # 第3条还在
        self.assertIsNotNone(purchase_service.get_purchase_by_id(p3))

    def test_batch_delete_empty_list(self):
        """测试批量删除空列表返回0"""
        count = purchase_service.batch_delete_purchases([])
        self.assertEqual(count, 0)

    def test_batch_delete_recalc_avg_cost(self):
        """测试批量删除后加权平均成本重算"""
        # 创建2条不同价格的采购
        p1 = purchase_service.create_purchase({
            'purchase_date': '2026-08-10', 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '问题4_重算1'
        })
        p2 = purchase_service.create_purchase({
            'purchase_date': '2026-08-11', 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '15', 'payment_type': 'cash',
            'notes': '问题4_重算2'
        })
        # avg = (50+150)/20 = 10
        product = product_service.get_product_by_id(self.product_id)
        self.assertEqual(product['avg_cost'], 10)

        # 删除单价15的那条，avg应该变成5
        purchase_service.batch_delete_purchases([p2])
        product = product_service.get_product_by_id(self.product_id)
        self.assertEqual(product['avg_cost'], 5)


class TestPurchaseBatchDeleteRoutes(unittest.TestCase):
    """测试采购批量删除路由（问题4）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM purchases WHERE notes LIKE '问题4路由_%'")
        execute("DELETE FROM products WHERE name LIKE '问题4路由_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题4路由_%'")
        cls.product_id = product_service.create_product({
            'name': '问题4路由_商品', 'purchase_price': '10'
        })
        cls.supplier_id = supplier_service.create_supplier({
            'name': '问题4路由_供应商'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM purchases WHERE notes LIKE '问题4路由_%'")
        execute("DELETE FROM products WHERE name LIKE '问题4路由_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题4路由_%'")

    def test_batch_delete_api(self):
        p1 = purchase_service.create_purchase({
            'purchase_date': '2026-08-12', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '5', 'unit_price': '10',
            'notes': '问题4路由_1'
        })
        p2 = purchase_service.create_purchase({
            'purchase_date': '2026-08-12', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '3', 'unit_price': '10',
            'notes': '问题4路由_2'
        })
        resp = self.client.post('/purchase/api/batch_delete', data={
            'ids': f'{p1},{p2}'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('2', data['message'])

    def test_batch_delete_api_no_ids(self):
        resp = self.client.post('/purchase/api/batch_delete', data={'ids': ''})
        self.assertFalse(resp.get_json()['success'])

    def test_purchase_page_has_checkboxes(self):
        resp = self.client.get('/purchase/')
        html = resp.get_data(as_text=True)
        self.assertIn('selectAll', html)
        self.assertIn('row-checkbox', html)
        self.assertIn('batchDelete', html)
        self.assertIn('批量删除', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
