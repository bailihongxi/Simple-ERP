import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import payment_service, supplier_service, customer_service, product_service, purchase_service, sales_service
from database.db import execute


class TestPaymentService(unittest.TestCase):
    """测试收付款服务层"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM payments WHERE notes LIKE '测试收付款_%'")
        execute("DELETE FROM sales WHERE notes LIKE '测试收付款销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试收付款采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试收付款商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '测试收付款供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '测试收付款客户_%'")

        cls.supplier_id = supplier_service.create_supplier({'name': '测试收付款供应商_1'})
        cls.customer_id = customer_service.create_customer({'name': '测试收付款客户_1'})
        cls.product_id = product_service.create_product({'name': '测试收付款商品_1', 'purchase_price': '5', 'sale_price': '10'})

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM payments WHERE notes LIKE '测试收付款_%'")
        execute("DELETE FROM sales WHERE notes LIKE '测试收付款销售_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '测试收付款采购_%'")
        execute("DELETE FROM products WHERE name LIKE '测试收付款商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '测试收付款供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '测试收付款客户_%'")

    def setUp(self):
        execute("DELETE FROM payments WHERE party_id IN (?, ?)", (self.supplier_id, self.customer_id))
        execute("DELETE FROM purchases WHERE supplier_id = ?", (self.supplier_id,))
        execute("DELETE FROM sales WHERE customer_id = ?", (self.customer_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))

    def test_supplier_payment_reduces_payable(self):
        """测试供应商付款后应付余额减少"""
        # 赊账采购100元
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '20', 'unit_price': '5',
            'payment_type': 'credit', 'notes': '测试收付款采购_赊账'
        })
        self.assertEqual(supplier_service.get_supplier_payable(self.supplier_id), 100)
        # 付款60元
        payment_service.create_payment({
            'payment_date': '2026-01-10', 'type': 'pay',
            'party_type': 'supplier', 'party_id': self.supplier_id,
            'amount': '60', 'notes': '测试收付款_付款'
        })
        self.assertEqual(supplier_service.get_supplier_payable(self.supplier_id), 40)

    def test_customer_receive_reduces_receivable(self):
        """测试客户收款后应收余额减少"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'quantity': '20', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '测试收付款采购_入库'
        })
        # 赊账销售80元
        sales_service.create_sale({
            'sale_date': '2026-01-05', 'product_id': self.product_id,
            'customer_id': self.customer_id, 'quantity': '8', 'unit_price': '10',
            'payment_type': 'credit', 'notes': '测试收付款销售_赊账'
        })
        self.assertEqual(customer_service.get_customer_receivable(self.customer_id), 80)
        # 收款50元
        payment_service.create_payment({
            'payment_date': '2026-01-10', 'type': 'receive',
            'party_type': 'customer', 'party_id': self.customer_id,
            'amount': '50', 'notes': '测试收付款_收款'
        })
        self.assertEqual(customer_service.get_customer_receivable(self.customer_id), 30)

    def test_invalid_amount_rejected(self):
        """测试金额为0或负数被拒绝"""
        with self.assertRaises(ValueError):
            payment_service.create_payment({
                'type': 'pay', 'party_type': 'supplier', 'party_id': self.supplier_id,
                'amount': '0', 'notes': '测试收付款_零金额'
            })
        with self.assertRaises(ValueError):
            payment_service.create_payment({
                'type': 'pay', 'party_type': 'supplier', 'party_id': self.supplier_id,
                'amount': '-10', 'notes': '测试收付款_负金额'
            })

    def test_type_validation(self):
        """测试收付款类型与往来对象匹配校验"""
        # 供应商不能是收款
        with self.assertRaises(ValueError):
            payment_service.create_payment({
                'type': 'receive', 'party_type': 'supplier', 'party_id': self.supplier_id,
                'amount': '10', 'notes': '测试收付款_类型错1'
            })
        # 客户不能是付款
        with self.assertRaises(ValueError):
            payment_service.create_payment({
                'type': 'pay', 'party_type': 'customer', 'party_id': self.customer_id,
                'amount': '10', 'notes': '测试收付款_类型错2'
            })

    def test_get_payments_filter(self):
        """测试按条件查询收付款记录"""
        payment_service.create_payment({
            'type': 'pay', 'party_type': 'supplier', 'party_id': self.supplier_id,
            'amount': '30', 'notes': '测试收付款_查询'
        })
        results = payment_service.get_payments(party_type='supplier', party_id=self.supplier_id)
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]['type'], 'pay')

    def test_total_receivable_payable(self):
        """测试总应收和总应付计算"""
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': self.product_id,
            'supplier_id': self.supplier_id, 'quantity': '10', 'unit_price': '5',
            'payment_type': 'credit', 'notes': '测试收付款采购_总计'
        })
        total_payable = payment_service.get_total_payable()
        self.assertGreaterEqual(total_payable, 50)

    def test_delete_payment(self):
        """测试删除收付款记录"""
        pid = payment_service.create_payment({
            'type': 'pay', 'party_type': 'supplier', 'party_id': self.supplier_id,
            'amount': '20', 'notes': '测试收付款_删除'
        })
        payment_service.delete_payment(pid)
        self.assertIsNone(payment_service.get_payment_by_id(pid))


class TestPaymentRoutes(unittest.TestCase):
    """测试收付款路由API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM payments WHERE notes LIKE '路由收付款_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '路由收付款供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '路由收付款客户_%'")
        cls.supplier_id = supplier_service.create_supplier({'name': '路由收付款供应商_1'})
        cls.customer_id = customer_service.create_customer({'name': '路由收付款客户_1'})

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM payments WHERE notes LIKE '路由收付款_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '路由收付款供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '路由收付款客户_%'")

    def test_supplier_pay_api(self):
        resp = self.client.post(f'/suppliers/api/pay/{self.supplier_id}', data={
            'payment_date': '2026-01-15', 'amount': '100',
            'notes': '路由收付款_供应商付款'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('id', data)

    def test_customer_receive_api(self):
        resp = self.client.post(f'/customers/api/receive/{self.customer_id}', data={
            'payment_date': '2026-01-15', 'amount': '50',
            'notes': '路由收付款_客户收款'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])

    def test_pay_api_invalid_amount(self):
        resp = self.client.post(f'/suppliers/api/pay/{self.supplier_id}', data={
            'amount': '0', 'notes': '路由收付款_无效'
        })
        self.assertFalse(resp.get_json()['success'])

    def test_supplier_detail_includes_payments(self):
        resp = self.client.get(f'/suppliers/api/detail/{self.supplier_id}')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('payments', data)

    def test_customer_detail_includes_payments(self):
        resp = self.client.get(f'/customers/api/detail/{self.customer_id}')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('payments', data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
