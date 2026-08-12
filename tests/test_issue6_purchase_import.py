import os
import sys
import unittest
import io

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service, supplier_service, purchase_service
from database.db import execute
from openpyxl import Workbook


class TestPurchaseImport(unittest.TestCase):
    """测试采购导入功能（问题6）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM purchases WHERE notes LIKE '问题6_%'")
        execute("DELETE FROM products WHERE name LIKE '问题6_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题6_%'")
        cls.product_id = product_service.create_product({
            'name': '问题6_导入商品', 'purchase_price': '10', 'sale_price': '20'
        })
        cls.supplier_id = supplier_service.create_supplier({
            'name': '问题6_导入供应商'
        })

    def setUp(self):
        execute("DELETE FROM purchases WHERE product_id = ?", (self.product_id,))
        execute("UPDATE products SET current_stock = 0, avg_cost = 0 WHERE id = ?", (self.product_id,))

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM purchases WHERE notes LIKE '问题6_%'")
        execute("DELETE FROM products WHERE name LIKE '问题6_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题6_%'")

    def _make_excel(self, rows):
        """创建Excel文件用于测试导入"""
        wb = Workbook()
        ws = wb.active
        ws.append(['商品名称*', '供应商名称', '采购日期*', '数量*', '单价*', '付款方式(现结/赊账)', '备注'])
        for row in rows:
            ws.append(row)
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf

    def test_import_template_download(self):
        """测试下载导入模板"""
        resp = self.client.get('/purchase/api/template')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_import_purchases_success(self):
        """测试成功导入多条采购记录"""
        buf = self._make_excel([
            ['问题6_导入商品', '问题6_导入供应商', '2026-08-12', '10', '5.5', '现结', '问题6_导入1'],
            ['问题6_导入商品', '问题6_导入供应商', '2026-08-13', '20', '6.0', '赊账', '问题6_导入2'],
        ])
        resp = self.client.post('/purchase/api/import', data={
            'file': (buf, 'test.xlsx')
        }, content_type='multipart/form-data')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['added'], 2)

        # 验证库存增加30
        product = product_service.get_product_by_id(self.product_id)
        self.assertEqual(product['current_stock'], 30)

    def test_import_product_not_exist(self):
        """测试导入时商品不存在的错误处理"""
        buf = self._make_excel([
            ['不存在的商品', '', '2026-08-12', '10', '5.5', '现结', '问题6_错误'],
        ])
        resp = self.client.post('/purchase/api/import', data={
            'file': (buf, 'test.xlsx')
        }, content_type='multipart/form-data')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['added'], 0)
        self.assertTrue(len(data['errors']) > 0)
        self.assertIn('不存在', data['errors'][0])

    def test_import_invalid_quantity(self):
        """测试导入时数量为0的错误处理"""
        buf = self._make_excel([
            ['问题6_导入商品', '', '2026-08-12', '0', '5.5', '现结', '问题6_数量0'],
        ])
        resp = self.client.post('/purchase/api/import', data={
            'file': (buf, 'test.xlsx')
        }, content_type='multipart/form-data')
        data = resp.get_json()
        self.assertEqual(data['added'], 0)

    def test_import_no_file(self):
        """测试未选择文件时的错误"""
        resp = self.client.post('/purchase/api/import', data={})
        self.assertFalse(resp.get_json()['success'])

    def test_purchase_page_has_import_button(self):
        """测试采购页面包含导入按钮"""
        resp = self.client.get('/purchase/')
        html = resp.get_data(as_text=True)
        self.assertIn('导入', html)
        self.assertIn('importFile', html)
        self.assertIn('doImport', html)
        self.assertIn('下载模板', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
