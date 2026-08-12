import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import inventory_service, product_service, purchase_service, sales_service
from database.db import execute


class TestInventoryService(unittest.TestCase):
    """测试库存服务层"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM inventory_adjustments WHERE reason LIKE '测试盘点_%'")
        execute("DELETE FROM sales WHERE notes LIKE '测试库存销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试库存采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试库存商品_%'")
        cls.product_id = product_service.create_product({
            'name': '测试库存商品_A', 'category': '库存测试', 'unit': '个',
            'purchase_price': '5', 'sale_price': '10', 'warning_stock': '5'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM inventory_adjustments WHERE reason LIKE '测试盘点_%'")
        execute("DELETE FROM sales WHERE notes LIKE '测试库存销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试库存采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试库存商品_%'")

    def setUp(self):
        execute("DELETE FROM inventory_adjustments WHERE product_id = ?", (self.product_id,))
        execute("DELETE FROM sales WHERE product_id = ?", (self.product_id,))
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))

    def test_inventory_list_stock_value(self):
        """测试库存列表包含库存价值计算"""
        # 采购入库：10个 × 5元
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试库存采购_价值'
        })
        items = inventory_service.get_inventory_list()
        item = next((i for i in items if i['id'] == self.product_id), None)
        self.assertIsNotNone(item)
        self.assertEqual(float(item['current_stock']), 10)
        self.assertAlmostEqual(float(item['avg_cost']), 5.0, places=2)
        self.assertAlmostEqual(float(item['stock_value']), 50.0, places=2)  # 10 × 5

    def test_inventory_summary(self):
        """测试库存汇总统计"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'quantity': '20', 'unit_price': '8', 'payment_type': 'cash',
            'notes': '测试库存采购_汇总'
        })
        summary = inventory_service.get_inventory_summary()
        self.assertGreaterEqual(summary['total_products'], 1)
        self.assertGreaterEqual(summary['total_stock'], 20)
        self.assertGreaterEqual(summary['total_value'], 160)

    def test_adjust_stock(self):
        """测试盘点调整库存"""
        # 先入库
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试库存采购_盘点'
        })
        # 盘点为7个
        change = inventory_service.adjust_stock(
            product_id=self.product_id,
            new_stock=7,
            reason='测试盘点_差异',
            notes='测试',
            adjust_date='2026-01-15'
        )
        self.assertEqual(change, -3)  # 7 - 10 = -3
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 7)
        # 验证盘点记录已插入
        logs = inventory_service.get_inventory_logs(product_id=self.product_id)
        adj_logs = [l for l in logs if l['type'] == 'adjust']
        self.assertTrue(len(adj_logs) >= 1)

    def test_adjust_stock_negative_rejected(self):
        """测试盘点为负库存被拒绝"""
        with self.assertRaises(ValueError):
            inventory_service.adjust_stock(
                product_id=self.product_id,
                new_stock=-5,
                reason='测试盘点_负数'
            )

    def test_low_stock_filter(self):
        """测试低库存筛选"""
        # warning_stock=5，库存设为3 → 低库存
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'quantity': '3', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试库存采购_低库存'
        })
        low_items = inventory_service.get_inventory_list(low_stock_only=True)
        ids = [i['id'] for i in low_items]
        self.assertIn(self.product_id, ids)

    def test_inventory_logs_includes_purchase_sale_adjust(self):
        """测试库存变动流水包含采购、销售、盘点三种类型"""
        # 采购
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'quantity': '20', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试库存采购_流水'
        })
        # 销售
        sales_service.create_sale({
            'sale_date': '2026-01-05', 'product_id': self.product_id,
            'quantity': '5', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '测试库存销售_流水'
        })
        # 盘点
        inventory_service.adjust_stock(
            product_id=self.product_id, new_stock=12,
            reason='测试盘点_流水', adjust_date='2026-01-10'
        )
        logs = inventory_service.get_inventory_logs(product_id=self.product_id)
        types = set(l['type'] for l in logs)
        self.assertIn('purchase', types)
        self.assertIn('sale', types)
        self.assertIn('adjust', types)
        # 验证销售变动为负
        sale_log = next(l for l in logs if l['type'] == 'sale')
        self.assertLess(sale_log['change_amount'], 0)

    def test_inventory_logs_ordered_by_date(self):
        """测试库存变动流水按日期倒序"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试库存采购_排序'
        })
        sales_service.create_sale({
            'sale_date': '2026-02-01', 'product_id': self.product_id,
            'quantity': '2', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '测试库存销售_排序'
        })
        logs = inventory_service.get_inventory_logs(product_id=self.product_id)
        self.assertEqual(logs[0]['type'], 'sale')  # 2月在最前


class TestInventoryRoutes(unittest.TestCase):
    """测试库存路由API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM inventory_adjustments WHERE reason LIKE '路由盘点_%'")
        execute("DELETE FROM products WHERE name LIKE '路由库存商品_%'")
        cls.product_id = product_service.create_product({
            'name': '路由库存商品_1', 'purchase_price': '5', 'warning_stock': '0'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM inventory_adjustments WHERE reason LIKE '路由盘点_%'")
        execute("DELETE FROM products WHERE name LIKE '路由库存商品_%'")

    def test_inventory_page_renders(self):
        resp = self.client.get('/inventory/')
        self.assertEqual(resp.status_code, 200)

    def test_adjust_api(self):
        resp = self.client.post('/inventory/api/adjust', data={
            'product_id': self.product_id, 'new_stock': '15',
            'reason': '路由盘点_测试', 'adjust_date': '2026-01-01'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 15)

    def test_adjust_api_missing_product(self):
        resp = self.client.post('/inventory/api/adjust', data={
            'new_stock': '10', 'reason': '测试'
        })
        self.assertFalse(resp.get_json()['success'])

    def test_logs_api(self):
        resp = self.client.get(f'/inventory/api/logs?product_id={self.product_id}')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)


if __name__ == '__main__':
    unittest.main(verbosity=2)
