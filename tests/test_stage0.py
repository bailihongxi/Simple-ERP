import os
import sys
import unittest
import tempfile
import sqlite3

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class TestDatabaseInit(unittest.TestCase):
    """测试数据库初始化"""

    def test_init_db_creates_tables(self):
        """测试 init_db 能创建所有 7 张表"""
        from database.db import init_db, get_db
        init_db()
        conn = get_db()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()
        expected = ['customers', 'inventory_adjustments', 'payments', 'products', 'purchases', 'sales', 'suppliers']
        for t in expected:
            self.assertIn(t, tables, f"表 {t} 未创建")

    def test_products_table_has_avg_cost(self):
        """测试 products 表包含加权平均成本字段"""
        from database.db import get_db
        conn = get_db()
        cursor = conn.execute("PRAGMA table_info(products)")
        columns = [row['name'] for row in cursor.fetchall()]
        conn.close()
        self.assertIn('avg_cost', columns)
        self.assertIn('current_stock', columns)
        self.assertIn('warning_stock', columns)

    def test_purchases_table_columns(self):
        """测试 purchases 表字段完整"""
        from database.db import get_db
        conn = get_db()
        cursor = conn.execute("PRAGMA table_info(purchases)")
        columns = [row['name'] for row in cursor.fetchall()]
        conn.close()
        for col in ['id', 'purchase_date', 'product_id', 'supplier_id', 'quantity', 'unit_price', 'total_amount', 'payment_type']:
            self.assertIn(col, columns)

    def test_sales_table_columns(self):
        """测试 sales 表字段完整（含成本和毛利）"""
        from database.db import get_db
        conn = get_db()
        cursor = conn.execute("PRAGMA table_info(sales)")
        columns = [row['name'] for row in cursor.fetchall()]
        conn.close()
        for col in ['id', 'sale_date', 'product_id', 'customer_id', 'quantity', 'unit_price', 'total_amount', 'cost_amount', 'profit', 'payment_type']:
            self.assertIn(col, columns)


class TestFlaskApp(unittest.TestCase):
    """测试 Flask 应用和路由"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_app_created(self):
        """测试 Flask 应用创建成功"""
        self.assertIsNotNone(self.app)

    def test_dashboard_route(self):
        """测试首页路由可访问"""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'\xe9\xa6\x96\xe9\xa1\xb5', resp.data)  # "首页" 的 UTF-8 编码

    def test_purchase_route(self):
        resp = self.client.get('/purchase/')
        self.assertEqual(resp.status_code, 200)

    def test_sales_route(self):
        resp = self.client.get('/sales/')
        self.assertEqual(resp.status_code, 200)

    def test_inventory_route(self):
        resp = self.client.get('/inventory/')
        self.assertEqual(resp.status_code, 200)

    def test_products_route(self):
        resp = self.client.get('/products/')
        self.assertEqual(resp.status_code, 200)

    def test_suppliers_route(self):
        resp = self.client.get('/suppliers/')
        self.assertEqual(resp.status_code, 200)

    def test_customers_route(self):
        resp = self.client.get('/customers/')
        self.assertEqual(resp.status_code, 200)

    def test_finance_route(self):
        resp = self.client.get('/finance/')
        self.assertEqual(resp.status_code, 200)

    def test_backup_route(self):
        resp = self.client.get('/backup/')
        self.assertEqual(resp.status_code, 200)

    def test_base_template_has_nav(self):
        """测试基础模板包含左侧导航"""
        resp = self.client.get('/')
        self.assertIn(b'\xe9\x87\x87\xe8\xb4\xad\xe7\xae\xa1\xe7\x90\x86', resp.data)  # 采购管理
        self.assertIn(b'\xe9\x94\x80\xe5\x94\xae\xe7\xae\xa1\xe7\x90\x86', resp.data)  # 销售管理
        self.assertIn(b'\xe5\xba\x93\xe5\xad\x98\xe7\xae\xa1\xe7\x90\x86', resp.data)  # 库存管理


class TestHelpers(unittest.TestCase):
    """测试工具函数"""

    def test_format_money(self):
        from utils.helpers import format_money
        self.assertEqual(format_money(1234.5), '1,234.50')
        self.assertEqual(format_money(0), '0.00')
        self.assertEqual(format_money(None), '0.00')

    def test_today_str(self):
        from utils.helpers import today_str
        import re
        self.assertTrue(re.match(r'\d{4}-\d{2}-\d{2}', today_str()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
