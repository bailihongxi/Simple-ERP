import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import (
    product_service, supplier_service, customer_service,
    purchase_service, sales_service, inventory_service,
    payment_service, finance_service, dashboard_service, backup_service
)
from database.db import execute, query_one


class TestEndToEndFlow(unittest.TestCase):
    """端到端业务流程测试"""

    @classmethod
    def setUpClass(cls):
        # 清理所有测试数据
        execute("DELETE FROM payments WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM sales WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM purchases WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM inventory_adjustments WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM products WHERE name LIKE 'E2E_%'")
        execute("DELETE FROM suppliers WHERE name LIKE 'E2E_%'")
        execute("DELETE FROM customers WHERE name LIKE 'E2E_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM payments WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM sales WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM purchases WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM inventory_adjustments WHERE notes LIKE 'E2E_%'")
        execute("DELETE FROM products WHERE name LIKE 'E2E_%'")
        execute("DELETE FROM suppliers WHERE name LIKE 'E2E_%'")
        execute("DELETE FROM customers WHERE name LIKE 'E2E_%'")

    def test_full_business_flow(self):
        """测试完整业务流程：建商品→采购→销售→库存→财务"""
        # 1. 创建基础数据
        supplier_id = supplier_service.create_supplier({'name': 'E2E_供应商A'})
        customer_id = customer_service.create_customer({'name': 'E2E_客户A'})
        product_id = product_service.create_product({
            'name': 'E2E_商品A', 'category': '测试', 'unit': '个',
            'purchase_price': '10', 'sale_price': '20', 'warning_stock': '5'
        })

        # 2. 第一次采购：10个，单价10元 → avg_cost=10, stock=10
        purchase_service.create_purchase({
            'purchase_date': '2026-01-01', 'product_id': product_id,
            'supplier_id': supplier_id, 'quantity': '10', 'unit_price': '10',
            'payment_type': 'cash', 'notes': 'E2E_采购1'
        })
        product = product_service.get_product_by_id(product_id)
        self.assertEqual(product['current_stock'], 10)
        self.assertEqual(product['avg_cost'], 10)

        # 3. 第二次采购：10个，单价20元 → avg_cost=(10*10+10*20)/20=15, stock=20
        purchase_service.create_purchase({
            'purchase_date': '2026-01-02', 'product_id': product_id,
            'supplier_id': supplier_id, 'quantity': '10', 'unit_price': '20',
            'payment_type': 'credit', 'notes': 'E2E_采购2'
        })
        product = product_service.get_product_by_id(product_id)
        self.assertEqual(product['current_stock'], 20)
        self.assertEqual(product['avg_cost'], 15)

        # 4. 销售：5个，单价20元 → 成本=5*15=75, 毛利=100-75=25, stock=15
        sale_id = sales_service.create_sale({
            'sale_date': '2026-01-03', 'product_id': product_id,
            'customer_id': customer_id, 'quantity': '5', 'unit_price': '20',
            'payment_type': 'credit', 'notes': 'E2E_销售1'
        })
        product = product_service.get_product_by_id(product_id)
        self.assertEqual(product['current_stock'], 15)
        self.assertEqual(product['avg_cost'], 15)  # 销售不改变avg_cost

        sale = sales_service.get_sale_by_id(sale_id)
        self.assertEqual(sale['cost_amount'], 75)
        self.assertEqual(sale['profit'], 25)

        # 5. 库存盘点：调整为12个
        inventory_service.adjust_stock(
            product_id=product_id, new_stock=12,
            reason='盘点', notes='E2E_盘点'
        )
        product = product_service.get_product_by_id(product_id)
        self.assertEqual(product['current_stock'], 12)

        # 6. 供应商付款：赊账采购200元，付款100元
        payment_service.create_payment({
            'payment_date': '2026-01-04', 'type': 'pay',
            'party_type': 'supplier', 'party_id': supplier_id,
            'amount': '100', 'notes': 'E2E_付款'
        })
        payable = supplier_service.get_supplier_payable(supplier_id)
        self.assertEqual(payable, 100)  # 200赊账 - 100付款 = 100

        # 7. 客户收款：赊账销售100元，收款50元
        payment_service.create_payment({
            'payment_date': '2026-01-05', 'type': 'receive',
            'party_type': 'customer', 'party_id': customer_id,
            'amount': '50', 'notes': 'E2E_收款'
        })
        receivable = customer_service.get_customer_receivable(customer_id)
        self.assertEqual(receivable, 50)  # 100赊账 - 50收款 = 50

        # 8. 财务汇总
        summary = finance_service.get_finance_summary(
            date_start='2026-01-01', date_end='2026-01-31'
        )
        self.assertGreater(summary['total_income'], 0)
        self.assertGreater(summary['total_expense'], 0)
        self.assertGreater(summary['gross_profit'], 0)

        # 9. 首页数据
        dashboard = dashboard_service.get_dashboard_data()
        self.assertIn('today_purchase', dashboard)
        self.assertIn('inventory_value', dashboard)

        # 10. 库存变动流水包含三种类型
        logs = inventory_service.get_inventory_logs(product_id=product_id)
        types = set(log['type'] for log in logs)
        self.assertIn('purchase', types)
        self.assertIn('sale', types)
        self.assertIn('adjust', types)

    def test_all_pages_accessible(self):
        """测试所有页面可访问"""
        from app import create_app
        app = create_app()
        client = app.test_client()
        pages = ['/', '/products/', '/suppliers/', '/customers/',
                 '/purchase/', '/sales/', '/inventory/', '/finance/', '/backup/']
        for page in pages:
            resp = client.get(page)
            self.assertEqual(resp.status_code, 200, f'页面 {page} 无法访问')

    def test_weighted_avg_cost_after_edit_purchase(self):
        """测试编辑采购后加权平均成本重算"""
        product_id = product_service.create_product({'name': 'E2E_加权测试商品'})
        # 采购1：10个@5元 → avg=5
        p1 = purchase_service.create_purchase({
            'purchase_date': '2026-02-01', 'product_id': product_id,
            'quantity': '10', 'unit_price': '5', 'payment_type': 'cash',
            'notes': 'E2E_加权采购1'
        })
        # 采购2：10个@15元 → avg=(50+150)/20=10
        purchase_service.create_purchase({
            'purchase_date': '2026-02-02', 'product_id': product_id,
            'quantity': '10', 'unit_price': '15', 'payment_type': 'cash',
            'notes': 'E2E_加权采购2'
        })
        product = product_service.get_product_by_id(product_id)
        self.assertEqual(product['avg_cost'], 10)

        # 编辑采购1：数量改为20@5元 → avg=(100+150)/30=8.33
        purchase_service.update_purchase(p1, {
            'purchase_date': '2026-02-01', 'product_id': product_id,
            'quantity': '20', 'unit_price': '5', 'payment_type': 'cash',
            'notes': 'E2E_加权采购1_编辑'
        })
        product = product_service.get_product_by_id(product_id)
        self.assertAlmostEqual(product['avg_cost'], 8.33, places=2)

    def test_delete_product_with_refs_blocked(self):
        """测试有关联记录的商品不可删除"""
        product_id = product_service.create_product({'name': 'E2E_删除测试商品'})
        purchase_service.create_purchase({
            'purchase_date': '2026-03-01', 'product_id': product_id,
            'quantity': '5', 'unit_price': '10', 'payment_type': 'cash',
            'notes': 'E2E_删除测试采购'
        })
        success, msg = product_service.delete_product(product_id)
        self.assertFalse(success)
        self.assertIn('关联', msg)

    def test_backup_restore_data_integrity(self):
        """测试备份恢复后数据完整性"""
        # 创建一个备份
        path = backup_service.create_backup()
        filename = os.path.basename(path)

        # 验证备份文件存在且非空
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)

        # 恢复（会自动备份当前数据）
        before_path = backup_service.restore_backup(filename)
        self.assertTrue(os.path.exists(before_path))

        # 验证数据库仍可正常查询
        products = product_service.get_products()
        self.assertIsInstance(products, list)

        # 清理
        os.remove(path)
        if os.path.exists(before_path):
            os.remove(before_path)


class TestAllModulesExport(unittest.TestCase):
    """测试所有模块导出功能"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_all_export_endpoints(self):
        endpoints = [
            '/products/api/export',
            '/suppliers/api/export',
            '/customers/api/export',
            '/purchase/api/export',
            '/sales/api/export',
            '/inventory/api/export',
            '/finance/api/export',
        ]
        for ep in endpoints:
            resp = self.client.get(ep)
            self.assertEqual(resp.status_code, 200, f'导出端点 {ep} 失败')
            self.assertIn('spreadsheet', resp.content_type, f'端点 {ep} 返回类型错误')


if __name__ == '__main__':
    unittest.main(verbosity=2)
