import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import purchase_service, product_service, supplier_service
from database.db import execute, query_one


class TestPurchaseService(unittest.TestCase):
    """测试采购服务层"""

    @classmethod
    def setUpClass(cls):
        # 清理测试数据
        execute("DELETE FROM purchases WHERE notes LIKE '测试采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试采购商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '测试采购供应商_%'")
        # 创建测试商品和供应商
        cls.product_id = product_service.create_product({
            'name': '测试采购商品_A', 'category': '测试', 'unit': '个',
            'purchase_price': '5', 'sale_price': '10', 'warning_stock': '0'
        })
        cls.supplier_id = supplier_service.create_supplier({
            'name': '测试采购供应商_1', 'contact_person': '测试'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM purchases WHERE notes LIKE '测试采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试采购商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '测试采购供应商_%'")

    def setUp(self):
        # 每个测试前重置商品库存和成本
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))

    def test_create_purchase_increases_stock(self):
        """测试新增采购后库存增加"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-15',
            'product_id': self.product_id,
            'supplier_id': self.supplier_id,
            'quantity': '10',
            'unit_price': '5',
            'payment_type': 'cash',
            'notes': '测试采购_增库存'
        })
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 10)

    def test_create_purchase_avg_cost_first(self):
        """测试首次采购后平均成本等于采购单价"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_首次'
        })
        p = product_service.get_product_by_id(self.product_id)
        self.assertAlmostEqual(float(p['avg_cost']), 5.0, places=2)

    def test_create_purchase_avg_cost_weighted(self):
        """测试多次采购后加权平均成本计算正确"""
        # 第一次：10个 × 5元
        purchase_service.create_purchase({
            'purchase_date': '2026-01-10', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_加权1'
        })
        # 第二次：10个 × 10元
        purchase_service.create_purchase({
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '10',
            'payment_type': 'cash', 'notes': '测试采购_加权2'
        })
        p = product_service.get_product_by_id(self.product_id)
        # (10*5 + 10*10) / 20 = 7.5
        self.assertAlmostEqual(float(p['avg_cost']), 7.5, places=2)
        self.assertEqual(float(p['current_stock']), 20)

    def test_update_purchase_adjusts_stock(self):
        """测试编辑采购数量后库存调整"""
        pid = purchase_service.create_purchase({
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_编辑'
        })
        # 编辑为数量15
        purchase_service.update_purchase(pid, {
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '15', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_编辑'
        })
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 15)

    def test_update_purchase_recalc_avg_cost(self):
        """测试编辑采购后加权平均成本重算"""
        # 第一次：10个 × 5元
        pid1 = purchase_service.create_purchase({
            'purchase_date': '2026-01-10', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_重算1'
        })
        # 第二次：10个 × 10元
        purchase_service.create_purchase({
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '10',
            'payment_type': 'cash', 'notes': '测试采购_重算2'
        })
        # 编辑第一次为20个 × 5元
        purchase_service.update_purchase(pid1, {
            'purchase_date': '2026-01-10', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '20', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_重算1'
        })
        p = product_service.get_product_by_id(self.product_id)
        # (20*5 + 10*10) / 30 = 6.666...
        self.assertAlmostEqual(float(p['avg_cost']), 6.6667, places=2)
        self.assertEqual(float(p['current_stock']), 30)

    def test_delete_purchase_rolls_back_stock(self):
        """测试删除采购后库存回退"""
        pid = purchase_service.create_purchase({
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_删除'
        })
        purchase_service.delete_purchase(pid)
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 0)
        self.assertAlmostEqual(float(p['avg_cost']), 0, places=2)

    def test_delete_purchase_recalc_avg_cost(self):
        """测试删除采购后平均成本重算"""
        # 第一次：10个 × 5元
        purchase_service.create_purchase({
            'purchase_date': '2026-01-10', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_删重算1'
        })
        # 第二次：10个 × 10元
        pid2 = purchase_service.create_purchase({
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '10',
            'payment_type': 'cash', 'notes': '测试采购_删重算2'
        })
        # 删除第二次
        purchase_service.delete_purchase(pid2)
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 10)
        self.assertAlmostEqual(float(p['avg_cost']), 5.0, places=2)

    def test_create_purchase_credit_affects_payable(self):
        """测试赊账采购影响供应商应付余额"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-15', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '5', 'unit_price': '10',
            'payment_type': 'credit', 'notes': '测试采购_赊账'
        })
        balance = supplier_service.get_supplier_payable(self.supplier_id)
        self.assertEqual(balance, 50)

    def test_invalid_quantity_rejected(self):
        """测试数量为0或负数被拒绝"""
        with self.assertRaises(ValueError):
            purchase_service.create_purchase({
                'purchase_date': '2026-01-15', 'product_id': self.product_id,
                'supplier_id': self.supplier_id, 'quantity': '0', 'unit_price': '5',
                'payment_type': 'cash', 'notes': '测试采购_无效数量'
            })
        with self.assertRaises(ValueError):
            purchase_service.create_purchase({
                'purchase_date': '2026-01-15', 'product_id': self.product_id,
                'supplier_id': self.supplier_id, 'quantity': '-5', 'unit_price': '5',
                'payment_type': 'cash', 'notes': '测试采购_负数量'
            })

    def test_get_purchases_filter_by_date(self):
        """测试按日期筛选采购记录"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-10', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '5', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试采购_日期筛选'
        })
        results = purchase_service.get_purchases(date_start='2026-01-01', date_end='2026-01-20')
        self.assertTrue(len(results) >= 1)
        results_empty = purchase_service.get_purchases(date_start='2025-01-01', date_end='2025-12-31')
        self.assertEqual(len(results_empty), 0)

    def test_purchase_stats(self):
        """测试采购统计"""
        purchase_service.create_purchase({
            'purchase_date': '2026-02-01', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '5', 'unit_price': '10',
            'payment_type': 'cash', 'notes': '测试采购_统计'
        })
        stats = purchase_service.get_purchase_stats(date_start='2026-02-01', date_end='2026-02-28')
        self.assertGreaterEqual(stats['total_amount'], 50)
        self.assertGreaterEqual(stats['count'], 1)


class TestPurchaseRoutes(unittest.TestCase):
    """测试采购路由API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM purchases WHERE notes LIKE '路由采购_%'")
        execute("DELETE FROM products WHERE name LIKE '路由采购商品_%'")
        cls.product_id = product_service.create_product({'name': '路由采购商品_1', 'purchase_price': '5'})

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM purchases WHERE notes LIKE '路由采购_%'")
        execute("DELETE FROM products WHERE name LIKE '路由采购商品_%'")

    def test_purchase_page_renders(self):
        resp = self.client.get('/purchase/')
        self.assertEqual(resp.status_code, 200)

    def test_create_api(self):
        resp = self.client.post('/purchase/api/create', data={
            'purchase_date': '2026-03-01', 'product_id': self.product_id,
            'quantity': '5', 'unit_price': '8', 'payment_type': 'cash',
            'notes': '路由采购_创建'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('id', data)

    def test_create_api_missing_product(self):
        resp = self.client.post('/purchase/api/create', data={
            'purchase_date': '2026-03-01', 'quantity': '5', 'unit_price': '8',
            'notes': '路由采购_缺商品'
        })
        self.assertFalse(resp.get_json()['success'])

    def test_delete_api(self):
        resp = self.client.post('/purchase/api/create', data={
            'purchase_date': '2026-03-01', 'product_id': self.product_id,
            'quantity': '3', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '路由采购_删除'
        })
        pid = resp.get_json()['id']
        resp2 = self.client.post(f'/purchase/api/delete/{pid}')
        self.assertTrue(resp2.get_json()['success'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
