import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service, customer_service, sales_service, purchase_service
from database.db import execute


class TestSalesBatchDelete(unittest.TestCase):
    """测试销售批量删除功能（问题5）"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '问题5_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '问题5_%'")
        execute("DELETE FROM products WHERE name LIKE '问题5_%'")
        execute("DELETE FROM customers WHERE name LIKE '问题5_%'")
        cls.product_id = product_service.create_product({
            'name': '问题5_批量商品', 'purchase_price': '5', 'sale_price': '20'
        })
        cls.customer_id = customer_service.create_customer({
            'name': '问题5_批量客户'
        })

    def setUp(self):
        # 每个测试前清理该商品的所有销售和采购记录，重置库存
        execute("DELETE FROM sales WHERE product_id = ?", (self.product_id,))
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))
        # 先采购100个@5元，确保库存充足
        purchase_service.create_purchase({
            'purchase_date': '2026-08-01', 'product_id': self.product_id,
            'quantity': '100', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '问题5_备货'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '问题5_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '问题5_%'")
        execute("DELETE FROM products WHERE name LIKE '问题5_%'")
        execute("DELETE FROM customers WHERE name LIKE '问题5_%'")

    def test_batch_delete_multiple_records(self):
        """测试批量删除多条销售记录"""
        s1 = sales_service.create_sale({
            'sale_date': '2026-08-12', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '5', 'unit_price': '20',
            'payment_type': 'cash', 'notes': '问题5_批量1'
        })
        s2 = sales_service.create_sale({
            'sale_date': '2026-08-12', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '10', 'unit_price': '20',
            'payment_type': 'cash', 'notes': '问题5_批量2'
        })
        s3 = sales_service.create_sale({
            'sale_date': '2026-08-12', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '15', 'unit_price': '20',
            'payment_type': 'cash', 'notes': '问题5_批量3'
        })

        product = product_service.get_product_by_id(self.product_id)
        stock_before = product['current_stock']  # 100-30=70

        # 批量删除前2条，回退库存15
        count = sales_service.batch_delete_sales([s1, s2])
        self.assertEqual(count, 2)

        product = product_service.get_product_by_id(self.product_id)
        self.assertEqual(product['current_stock'], stock_before + 15)  # 70+15=85

        self.assertIsNone(sales_service.get_sale_by_id(s1))
        self.assertIsNone(sales_service.get_sale_by_id(s2))
        self.assertIsNotNone(sales_service.get_sale_by_id(s3))

    def test_batch_delete_empty_list(self):
        """测试批量删除空列表返回0"""
        count = sales_service.batch_delete_sales([])
        self.assertEqual(count, 0)


class TestSalesBatchDeleteRoutes(unittest.TestCase):
    """测试销售批量删除路由（问题5）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM sales WHERE notes LIKE '问题5路由_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '问题5路由_%'")
        execute("DELETE FROM products WHERE name LIKE '问题5路由_%'")
        execute("DELETE FROM customers WHERE name LIKE '问题5路由_%'")
        cls.product_id = product_service.create_product({
            'name': '问题5路由_商品', 'purchase_price': '5', 'sale_price': '20'
        })
        cls.customer_id = customer_service.create_customer({
            'name': '问题5路由_客户'
        })
        purchase_service.create_purchase({
            'purchase_date': '2026-08-01', 'product_id': cls.product_id,
            'quantity': '100', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '问题5路由_备货'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '问题5路由_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '问题5路由_%'")
        execute("DELETE FROM products WHERE name LIKE '问题5路由_%'")
        execute("DELETE FROM customers WHERE name LIKE '问题5路由_%'")

    def test_batch_delete_api(self):
        s1 = sales_service.create_sale({
            'sale_date': '2026-08-12', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '5', 'unit_price': '20',
            'notes': '问题5路由_1'
        })
        s2 = sales_service.create_sale({
            'sale_date': '2026-08-12', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '3', 'unit_price': '20',
            'notes': '问题5路由_2'
        })
        resp = self.client.post('/sales/api/batch_delete', data={'ids': f'{s1},{s2}'})
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('2', data['message'])

    def test_batch_delete_api_no_ids(self):
        resp = self.client.post('/sales/api/batch_delete', data={'ids': ''})
        self.assertFalse(resp.get_json()['success'])

    def test_sales_page_has_checkboxes(self):
        resp = self.client.get('/sales/')
        html = resp.get_data(as_text=True)
        self.assertIn('selectAll', html)
        self.assertIn('row-checkbox', html)
        self.assertIn('batchDelete', html)
        self.assertIn('批量删除', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
