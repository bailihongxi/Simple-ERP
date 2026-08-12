import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import dashboard_service, product_service, purchase_service, sales_service
from database.db import execute
from utils.helpers import today_str


class TestDashboardService(unittest.TestCase):
    """测试首页服务层"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '测试首页销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试首页采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试首页商品_%'")
        cls.product_id = product_service.create_product({
            'name': '测试首页商品_1', 'purchase_price': '5', 'sale_price': '10',
            'warning_stock': '2'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '测试首页销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试首页采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试首页商品_%'")

    def setUp(self):
        execute("DELETE FROM sales WHERE product_id = ?", (self.product_id,))
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))

    def test_dashboard_data_structure(self):
        """测试首页数据结构完整"""
        data = dashboard_service.get_dashboard_data()
        self.assertIn('today_purchase', data)
        self.assertIn('today_sale', data)
        self.assertIn('month_purchase', data)
        self.assertIn('month_sale', data)
        self.assertIn('inventory_value', data)
        self.assertIn('total_receivable', data)
        self.assertIn('total_payable', data)
        self.assertIn('low_stock', data)
        self.assertIn('recent_transactions', data)

    def test_today_purchase_counted(self):
        """测试今日采购被统计"""
        today = today_str()
        purchase_service.create_purchase({
            'purchase_date': today, 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试首页采购_今日'
        })
        data = dashboard_service.get_dashboard_data()
        self.assertGreaterEqual(data['today_purchase']['count'], 1)
        self.assertGreaterEqual(data['today_purchase']['total'], 50)

    def test_today_sale_counted(self):
        """测试今日销售被统计"""
        today = today_str()
        purchase_service.create_purchase({
            'purchase_date': today, 'product_id': self.product_id,
            'quantity': '20', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试首页采购_入库'
        })
        sales_service.create_sale({
            'sale_date': today, 'product_id': self.product_id,
            'quantity': '5', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '测试首页销售_今日'
        })
        data = dashboard_service.get_dashboard_data()
        self.assertGreaterEqual(data['today_sale']['count'], 1)
        self.assertGreaterEqual(data['today_sale']['total'], 50)

    def test_low_stock_detection(self):
        """测试低库存预警检测"""
        # 设置很大的预警值，确保缺口最大，一定排在前10
        execute("UPDATE products SET warning_stock = 99999, current_stock = 0 WHERE id = ?", (self.product_id,))
        data = dashboard_service.get_dashboard_data()
        ids = [item['id'] for item in data['low_stock']]
        self.assertIn(self.product_id, ids)

    def test_recent_transactions_includes_both_types(self):
        """测试近期交易包含采购和销售"""
        today = today_str()
        purchase_service.create_purchase({
            'purchase_date': today, 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试首页采购_近期'
        })
        sales_service.create_sale({
            'sale_date': today, 'product_id': self.product_id,
            'quantity': '3', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '测试首页销售_近期'
        })
        data = dashboard_service.get_dashboard_data()
        types = set(t['type'] for t in data['recent_transactions'])
        self.assertIn('purchase', types)
        self.assertIn('sale', types)

    def test_recent_transactions_limited_10(self):
        """测试近期交易最多10条"""
        data = dashboard_service.get_dashboard_data()
        self.assertLessEqual(len(data['recent_transactions']), 10)


class TestDashboardRoutes(unittest.TestCase):
    """测试首页路由"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_dashboard_page_renders(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_api(self):
        resp = self.client.get('/api/dashboard')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('today_purchase', data['data'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
