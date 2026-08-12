import os
import sys
import unittest
import io

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service, customer_service, sales_service, purchase_service
from database.db import execute
from openpyxl import Workbook


class TestSalesImport(unittest.TestCase):
    """测试销售导入功能（问题7）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM sales WHERE notes LIKE '问题7_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '问题7_%'")
        execute("DELETE FROM products WHERE name LIKE '问题7_%'")
        execute("DELETE FROM customers WHERE name LIKE '问题7_%'")
        cls.product_id = product_service.create_product({
            'name': '问题7_导入商品', 'purchase_price': '5', 'sale_price': '20'
        })
        cls.customer_id = customer_service.create_customer({
            'name': '问题7_导入客户'
        })

    def setUp(self):
        execute("DELETE FROM sales WHERE product_id = ?", (self.product_id,))
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))
        # 备货100个
        purchase_service.create_purchase({
            'purchase_date': '2026-08-01', 'product_id': self.product_id,
            'quantity': '100', 'unit_price': '5', 'payment_type': 'cash',
            'notes': '问题7_备货'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '问题7_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '问题7_%'")
        execute("DELETE FROM products WHERE name LIKE '问题7_%'")
        execute("DELETE FROM customers WHERE name LIKE '问题7_%'")

    def _make_excel(self, rows):
        wb = Workbook()
        ws = wb.active
        ws.append(['商品名称*', '客户名称', '销售日期*', '数量*', '单价*', '付款方式(现结/赊账)', '备注'])
        for row in rows:
            ws.append(row)
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf

    def test_import_template_download(self):
        resp = self.client.get('/sales/api/template')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_import_sales_success(self):
        buf = self._make_excel([
            ['问题7_导入商品', '问题7_导入客户', '2026-08-12', '10', '20', '现结', '问题7_导入1'],
            ['问题7_导入商品', '问题7_导入客户', '2026-08-13', '20', '25', '赊账', '问题7_导入2'],
        ])
        resp = self.client.post('/sales/api/import', data={
            'file': (buf, 'test.xlsx')
        }, content_type='multipart/form-data')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['added'], 2)

        product = product_service.get_product_by_id(self.product_id)
        self.assertEqual(product['current_stock'], 70)  # 100-30

    def test_import_insufficient_stock(self):
        """测试导入时库存不足的错误处理"""
        buf = self._make_excel([
            ['问题7_导入商品', '', '2026-08-12', '200', '20', '现结', '问题7_库存不足'],
        ])
        resp = self.client.post('/sales/api/import', data={
            'file': (buf, 'test.xlsx')
        }, content_type='multipart/form-data')
        data = resp.get_json()
        self.assertEqual(data['added'], 0)
        self.assertTrue(len(data['errors']) > 0)
        self.assertIn('库存不足', data['errors'][0])

    def test_import_product_not_exist(self):
        buf = self._make_excel([
            ['不存在的商品', '', '2026-08-12', '10', '20', '现结', '问题7_错误'],
        ])
        resp = self.client.post('/sales/api/import', data={
            'file': (buf, 'test.xlsx')
        }, content_type='multipart/form-data')
        data = resp.get_json()
        self.assertEqual(data['added'], 0)

    def test_import_no_file(self):
        resp = self.client.post('/sales/api/import', data={})
        self.assertFalse(resp.get_json()['success'])

    def test_sales_page_has_import_button(self):
        resp = self.client.get('/sales/')
        html = resp.get_data(as_text=True)
        self.assertIn('导入', html)
        self.assertIn('importFile', html)
        self.assertIn('doImport', html)
        self.assertIn('下载模板', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
