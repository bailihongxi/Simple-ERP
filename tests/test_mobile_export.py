import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import mobile_service, product_service, purchase_service, sales_service
from database.db import execute


class TestMobileExportService(unittest.TestCase):
    """测试手机端数据导出服务（第二阶段功能1）"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '手机端测试_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '手机端测试_%'")
        execute("DELETE FROM products WHERE name LIKE '手机端测试_%'")
        cls.product_id = product_service.create_product({
            'name': '手机端测试_商品A', 'brand': '测试品牌',
            'category': '测试分类', 'purchase_price': '10', 'sale_price': '20'
        })
        purchase_service.create_purchase({
            'purchase_date': '2026-08-13', 'product_id': cls.product_id,
            'quantity': '10', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '手机端测试_采购1'
        })
        sales_service.create_sale({
            'sale_date': '2026-08-13', 'product_id': cls.product_id,
            'quantity': '3', 'unit_price': '20', 'payment_type': 'cash',
            'notes': '手机端测试_销售1'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '手机端测试_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '手机端测试_%'")
        execute("DELETE FROM products WHERE name LIKE '手机端测试_%'")

    def test_export_returns_valid_json(self):
        """测试导出返回有效的JSON"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        self.assertIsInstance(data, dict)

    def test_export_contains_required_fields(self):
        """测试导出包含所有必需的字段"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        self.assertIn('version', data)
        self.assertIn('export_time', data)
        self.assertIn('products', data)
        self.assertIn('purchases', data)
        self.assertIn('sales', data)
        self.assertIn('suppliers', data)
        self.assertIn('customers', data)
        self.assertIn('summary', data)

    def test_export_products_contains_data(self):
        """测试导出的产品数据包含测试商品"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        names = [p['name'] for p in data['products']]
        self.assertIn('手机端测试_商品A', names)

    def test_export_products_has_stock_info(self):
        """测试导出的产品数据包含库存和成本信息"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        product = next(p for p in data['products'] if p['name'] == '手机端测试_商品A')
        self.assertIn('current_stock', product)
        self.assertIn('avg_cost', product)
        self.assertIn('brand', product)
        self.assertIn('category', product)

    def test_export_purchases_contains_data(self):
        """测试导出的采购数据包含测试记录"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        notes = [p['notes'] for p in data['purchases']]
        self.assertIn('手机端测试_采购1', notes)

    def test_export_purchases_has_names(self):
        """测试导出的采购数据包含商品名称和供应商名称"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        purchase = next(p for p in data['purchases'] if p['notes'] == '手机端测试_采购1')
        self.assertIn('product_name', purchase)
        self.assertEqual(purchase['product_name'], '手机端测试_商品A')

    def test_export_sales_contains_data(self):
        """测试导出的销售数据包含测试记录"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        notes = [s['notes'] for s in data['sales']]
        self.assertIn('手机端测试_销售1', notes)

    def test_export_sales_has_profit_and_cost(self):
        """测试导出的销售数据包含成本和利润"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        sale = next(s for s in data['sales'] if s['notes'] == '手机端测试_销售1')
        self.assertIn('cost_amount', sale)
        self.assertIn('profit', sale)
        self.assertIn('product_name', sale)

    def test_export_summary_counts(self):
        """测试导出的汇总数据数量正确"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        self.assertGreaterEqual(data['summary']['product_count'], 1)
        self.assertGreaterEqual(data['summary']['purchase_count'], 1)
        self.assertGreaterEqual(data['summary']['sale_count'], 1)


class TestMobileExportRoutes(unittest.TestCase):
    """测试手机端数据导出路由（第二阶段功能1）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_export_mobile_api_returns_json(self):
        """测试导出API返回JSON文件"""
        resp = self.client.get('/backup/api/export_mobile')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('json', resp.content_type)
        # 验证是有效的JSON
        data = json.loads(resp.get_data(as_text=True))
        self.assertIn('products', data)
        self.assertIn('purchases', data)
        self.assertIn('sales', data)

    def test_backup_page_has_export_mobile_button(self):
        """测试备份页面包含导出手机端数据按钮"""
        resp = self.client.get('/backup/')
        html = resp.get_data(as_text=True)
        self.assertIn('导出手机端数据', html)
        self.assertIn('exportMobile', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
