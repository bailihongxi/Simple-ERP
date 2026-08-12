import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import sales_service, purchase_service, product_service, customer_service
from database.db import execute


class TestSalesService(unittest.TestCase):
    """测试销售服务层"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '测试销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试销售采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试销售商品_%'")
        execute("DELETE FROM customers WHERE name LIKE '测试销售客户_%'")
        cls.product_id = product_service.create_product({
            'name': '测试销售商品_A', 'category': '测试', 'unit': '个',
            'purchase_price': '5', 'sale_price': '15', 'warning_stock': '0'
        })
        cls.customer_id = customer_service.create_customer({
            'name': '测试销售客户_1', 'contact_person': '测试'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '测试销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试销售采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试销售商品_%'")
        execute("DELETE FROM customers WHERE name LIKE '测试销售客户_%'")

    def setUp(self):
        # 每个测试前重置：清销售、清采购、重置库存成本
        execute("DELETE FROM sales WHERE product_id = ?", (self.product_id,))
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))

    def _stock_up(self, quantity, unit_price, date='2026-01-01'):
        """辅助方法：采购入库"""
        purchase_service.create_purchase({
            'purchase_date': date, 'product_id': self.product_id,
            'supplier_id': None, 'quantity': str(quantity),
            'unit_price': str(unit_price), 'payment_type': 'cash',
            'notes': '测试销售采购_入库'
        })

    def test_create_sale_decreases_stock(self):
        """测试新增销售后库存减少"""
        self._stock_up(20, 5)
        sales_service.create_sale({
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '5',
            'unit_price': '15', 'payment_type': 'cash',
            'notes': '测试销售_减库存'
        })
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 15)

    def test_sale_cost_uses_avg_cost(self):
        """测试销售成本使用加权平均成本，而非默认进货价"""
        # 采购：10个×5元 + 10个×10元 → 平均成本7.5
        self._stock_up(10, 5, '2026-01-01')
        self._stock_up(10, 10, '2026-01-05')
        p = product_service.get_product_by_id(self.product_id)
        self.assertAlmostEqual(float(p['avg_cost']), 7.5, places=2)
        # 销售5个，单价20
        sid = sales_service.create_sale({
            'sale_date': '2026-01-10', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '5', 'unit_price': '20',
            'payment_type': 'cash', 'notes': '测试销售_成本'
        })
        sale = sales_service.get_sale_by_id(sid)
        # 成本 = 5 × 7.5 = 37.5
        self.assertAlmostEqual(float(sale['cost_amount']), 37.5, places=2)
        # 毛利 = 100 - 37.5 = 62.5
        self.assertAlmostEqual(float(sale['profit']), 62.5, places=2)

    def test_sale_insufficient_stock_rejected(self):
        """测试库存不足时销售被阻止"""
        self._stock_up(5, 5)
        with self.assertRaises(ValueError) as ctx:
            sales_service.create_sale({
                'sale_date': '2026-01-15', 'product_id': self.product_id,
                'customer_id': None, 'quantity': '10', 'unit_price': '15',
                'payment_type': 'cash', 'notes': '测试销售_超卖'
            })
        self.assertIn('库存不足', str(ctx.exception))

    def test_sale_does_not_change_avg_cost(self):
        """测试销售不改变加权平均成本"""
        self._stock_up(10, 5)
        self._stock_up(10, 10)
        p_before = product_service.get_product_by_id(self.product_id)
        avg_before = float(p_before['avg_cost'])
        sales_service.create_sale({
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '5', 'unit_price': '20',
            'payment_type': 'cash', 'notes': '测试销售_不改成本'
        })
        p_after = product_service.get_product_by_id(self.product_id)
        self.assertAlmostEqual(float(p_after['avg_cost']), avg_before, places=4)

    def test_update_sale_adjusts_stock(self):
        """测试编辑销售数量后库存调整"""
        self._stock_up(20, 5)
        sid = sales_service.create_sale({
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '5', 'unit_price': '15',
            'payment_type': 'cash', 'notes': '测试销售_编辑'
        })
        # 编辑为销售8个
        sales_service.update_sale(sid, {
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '8', 'unit_price': '15',
            'payment_type': 'cash', 'notes': '测试销售_编辑'
        })
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 12)  # 20 - 8

    def test_update_sale_recalc_cost_profit(self):
        """测试编辑销售后成本和利润用当前平均成本重算"""
        self._stock_up(10, 5)
        self._stock_up(10, 10)  # avg=7.5
        sid = sales_service.create_sale({
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '5', 'unit_price': '20',
            'payment_type': 'cash', 'notes': '测试销售_重算'
        })
        # 编辑数量为4，单价改为25
        sales_service.update_sale(sid, {
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '4', 'unit_price': '25',
            'payment_type': 'cash', 'notes': '测试销售_重算'
        })
        sale = sales_service.get_sale_by_id(sid)
        # 成本 = 4 × 7.5 = 30
        self.assertAlmostEqual(float(sale['cost_amount']), 30.0, places=2)
        # 毛利 = 100 - 30 = 70
        self.assertAlmostEqual(float(sale['profit']), 70.0, places=2)

    def test_delete_sale_rolls_back_stock(self):
        """测试删除销售后库存回退"""
        self._stock_up(20, 5)
        sid = sales_service.create_sale({
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '5', 'unit_price': '15',
            'payment_type': 'cash', 'notes': '测试销售_删除'
        })
        sales_service.delete_sale(sid)
        p = product_service.get_product_by_id(self.product_id)
        self.assertEqual(float(p['current_stock']), 20)

    def test_credit_sale_affects_receivable(self):
        """测试赊账销售影响客户应收余额"""
        self._stock_up(20, 5)
        sales_service.create_sale({
            'sale_date': '2026-01-15', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '5',
            'unit_price': '10', 'payment_type': 'credit',
            'notes': '测试销售_赊账'
        })
        balance = customer_service.get_customer_receivable(self.customer_id)
        self.assertEqual(balance, 50)

    def test_invalid_quantity_rejected(self):
        """测试数量为0或负数被拒绝"""
        self._stock_up(10, 5)
        with self.assertRaises(ValueError):
            sales_service.create_sale({
                'sale_date': '2026-01-15', 'product_id': self.product_id,
                'quantity': '0', 'unit_price': '10', 'payment_type': 'cash',
                'notes': '测试销售_零数量'
            })

    def test_sales_stats(self):
        """测试销售统计"""
        self._stock_up(20, 5)
        sales_service.create_sale({
            'sale_date': '2026-03-01', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '5', 'unit_price': '15',
            'payment_type': 'cash', 'notes': '测试销售_统计'
        })
        stats = sales_service.get_sales_stats(date_start='2026-03-01', date_end='2026-03-31')
        self.assertGreaterEqual(stats['total_amount'], 75)
        self.assertGreaterEqual(stats['total_profit'], 0)
        self.assertGreaterEqual(stats['count'], 1)

    def test_get_sales_filter(self):
        """测试销售记录筛选"""
        self._stock_up(20, 5)
        sales_service.create_sale({
            'sale_date': '2026-04-01', 'product_id': self.product_id,
            'customer_id': None, 'quantity': '2', 'unit_price': '15',
            'payment_type': 'cash', 'notes': '测试销售_筛选'
        })
        results = sales_service.get_sales(date_start='2026-04-01', date_end='2026-04-30')
        self.assertTrue(len(results) >= 1)


class TestSalesRoutes(unittest.TestCase):
    """测试销售路由API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM sales WHERE notes LIKE '路由销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '路由销售采购_%'")
        execute("DELETE FROM products WHERE name LIKE '路由销售商品_%'")
        cls.product_id = product_service.create_product({'name': '路由销售商品_1', 'purchase_price': '5', 'sale_price': '15'})
        # 入库
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': cls.product_id,
            'quantity': '100', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '路由销售采购_入库'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '路由销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '路由销售采购_%'")
        execute("DELETE FROM products WHERE name LIKE '路由销售商品_%'")

    def test_sales_page_renders(self):
        resp = self.client.get('/sales/')
        self.assertEqual(resp.status_code, 200)

    def test_create_api(self):
        resp = self.client.post('/sales/api/create', data={
            'sale_date': '2026-05-01', 'product_id': self.product_id,
            'quantity': '3', 'unit_price': '15', 'payment_type': 'cash',
            'notes': '路由销售_创建'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('id', data)

    def test_create_api_insufficient_stock(self):
        resp = self.client.post('/sales/api/create', data={
            'sale_date': '2026-05-01', 'product_id': self.product_id,
            'quantity': '99999', 'unit_price': '15', 'payment_type': 'cash',
            'notes': '路由销售_超卖'
        })
        self.assertFalse(resp.get_json()['success'])

    def test_delete_api(self):
        resp = self.client.post('/sales/api/create', data={
            'sale_date': '2026-05-01', 'product_id': self.product_id,
            'quantity': '2', 'unit_price': '15', 'payment_type': 'cash',
            'notes': '路由销售_删除'
        })
        sid = resp.get_json()['id']
        resp2 = self.client.post(f'/sales/api/delete/{sid}')
        self.assertTrue(resp2.get_json()['success'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
