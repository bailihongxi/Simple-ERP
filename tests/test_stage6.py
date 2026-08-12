import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import finance_service, product_service, supplier_service, customer_service, purchase_service, sales_service, payment_service
from database.db import execute


class TestFinanceService(unittest.TestCase):
    """测试财务服务层"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM payments WHERE notes LIKE '测试财务_%'")
        execute("DELETE FROM sales WHERE notes LIKE '测试财务销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试财务采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试财务商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '测试财务供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '测试财务客户_%'")

        cls.product_id = product_service.create_product({'name': '测试财务商品_1', 'purchase_price': '5', 'sale_price': '10'})
        cls.supplier_id = supplier_service.create_supplier({'name': '测试财务供应商_1'})
        cls.customer_id = customer_service.create_customer({'name': '测试财务客户_1'})

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM payments WHERE notes LIKE '测试财务_%'")
        execute("DELETE FROM sales WHERE notes LIKE '测试财务销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试财务采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试财务商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '测试财务供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '测试财务客户_%'")

    def setUp(self):
        execute("DELETE FROM payments WHERE party_id IN (?, ?)", (self.supplier_id, self.customer_id))
        execute("DELETE FROM purchases WHERE supplier_id = ? OR product_id = ?", (self.supplier_id, self.product_id))
        execute("DELETE FROM sales WHERE customer_id = ? OR product_id = ?", (self.customer_id, self.product_id))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))

    def test_finance_summary_income_expense(self):
        """测试财务汇总的收入和支出计算"""
        # 现结采购100元（支出）
        purchase_service.create_purchase({
            'purchase_date': '2026-06-01', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '20', 'unit_price': '5',
            'payment_type': 'cash', 'notes': '测试财务采购_现结'
        })
        # 现结销售150元（收入），成本100，毛利50
        sales_service.create_sale({
            'sale_date': '2026-06-05', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '15', 'unit_price': '10',
            'payment_type': 'cash', 'notes': '测试财务销售_现结'
        })
        summary = finance_service.get_finance_summary(
            date_start='2026-06-01', date_end='2026-06-30'
        )
        self.assertGreaterEqual(summary['total_income'], 150)
        self.assertGreaterEqual(summary['total_expense'], 100)
        self.assertGreaterEqual(summary['gross_profit'], 50)

    def test_finance_summary_includes_payments(self):
        """测试财务汇总包含收付款记录"""
        # 供应商付款50（支出）
        payment_service.create_payment({
            'payment_date': '2026-06-10', 'type': 'pay',
            'party_type': 'supplier', 'party_id': self.supplier_id,
            'amount': '50', 'notes': '测试财务_付款'
        })
        # 客户收款30（收入）
        payment_service.create_payment({
            'payment_date': '2026-06-15', 'type': 'receive',
            'party_type': 'customer', 'party_id': self.customer_id,
            'amount': '30', 'notes': '测试财务_收款'
        })
        summary = finance_service.get_finance_summary(
            date_start='2026-06-01', date_end='2026-06-30'
        )
        self.assertGreaterEqual(summary['paid'], 50)
        self.assertGreaterEqual(summary['received'], 30)

    def test_finance_summary_receivable_payable(self):
        """测试财务汇总包含应收应付总额"""
        summary = finance_service.get_finance_summary()
        self.assertIn('total_receivable', summary)
        self.assertIn('total_payable', summary)

    def test_payment_records_filter(self):
        """测试收付款记录查询和筛选"""
        payment_service.create_payment({
            'payment_date': '2026-06-01', 'type': 'pay',
            'party_type': 'supplier', 'party_id': self.supplier_id,
            'amount': '20', 'notes': '测试财务_记录筛选'
        })
        records = finance_service.get_payment_records(
            date_start='2026-06-01', date_end='2026-06-30', ptype='pay'
        )
        self.assertTrue(len(records) >= 1)
        self.assertEqual(records[0]['type'], 'pay')

    def test_monthly_trend(self):
        """测试月度趋势返回6个月数据"""
        trend = finance_service.get_monthly_trend(6)
        self.assertEqual(len(trend), 6)
        for t in trend:
            self.assertIn('month', t)
            self.assertIn('income', t)
            self.assertIn('expense', t)
            self.assertIn('gross_profit', t)

    def test_gross_margin_calculation(self):
        """测试毛利率计算"""
        purchase_service.create_purchase({
            'purchase_date': '2026-07-01', 'product_id': self.product_id,
            'quantity': '10', 'unit_price': '6', 'payment_type': 'cash',
            'notes': '测试财务采购_毛利'
        })
        sales_service.create_sale({
            'sale_date': '2026-07-05', 'product_id': self.product_id,
            'quantity': '5', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '测试财务销售_毛利'
        })
        summary = finance_service.get_finance_summary(
            date_start='2026-07-01', date_end='2026-07-31'
        )
        # 销售50，成本30，毛利20，毛利率40%
        self.assertGreater(summary['gross_margin'], 0)
        self.assertLessEqual(summary['gross_margin'], 100)


class TestFinanceRoutes(unittest.TestCase):
    """测试财务路由API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_finance_page_renders(self):
        resp = self.client.get('/finance/')
        self.assertEqual(resp.status_code, 200)

    def test_summary_api(self):
        resp = self.client.get('/finance/api/summary?date_start=2026-01-01&date_end=2026-12-31')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('total_income', data['data'])
        self.assertIn('total_expense', data['data'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
