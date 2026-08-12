import os
import sys
import io
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from utils.excel import export_to_excel, import_from_excel, export_with_key_mapping
from services import product_service, supplier_service, customer_service
from database.db import execute


class TestExcelUtils(unittest.TestCase):
    """测试Excel工具函数"""

    def test_export_to_excel_generates_valid_xlsx(self):
        """测试导出生成有效的xlsx内容"""
        headers = ['名称', '数量']
        rows = [['商品A', 10], ['商品B', 20]]
        content, filename = export_to_excel(headers, rows, 'test.xlsx')
        self.assertIsInstance(content, bytes)
        self.assertGreater(len(content), 0)
        self.assertEqual(filename, 'test.xlsx')
        # xlsx文件以PK开头（zip格式）
        self.assertTrue(content[:2] == b'PK')

    def test_export_with_key_mapping(self):
        """测试带字段映射的导出"""
        mapping = [('显示名', 'name'), ('数量', 'qty')]
        rows = [{'name': 'A', 'qty': 5}, {'name': 'B', 'qty': 8}]
        content, filename = export_with_key_mapping(mapping, rows, 'mapped.xlsx')
        self.assertIsInstance(content, bytes)
        self.assertGreater(len(content), 0)

    def test_import_from_excel_reads_data(self):
        """测试从Excel导入读取数据"""
        # 先生成一个Excel，再读取
        headers = ['商品名称', '数量']
        rows = [['测试商品', 15]]
        content, _ = export_to_excel(headers, rows)

        # 模拟Flask的file_storage
        class FakeFile:
            def __init__(self, data):
                self._data = data
            def read(self):
                return self._data

        fake_file = FakeFile(content)
        read_headers, read_rows = import_from_excel(fake_file)
        self.assertEqual(read_headers, ['商品名称', '数量'])
        self.assertEqual(len(read_rows), 1)
        self.assertEqual(read_rows[0]['商品名称'], '测试商品')

    def test_import_empty_file(self):
        """测试导入空文件"""
        headers = []
        rows = []
        content, _ = export_to_excel(headers, rows)
        class FakeFile:
            def __init__(self, data): self._data = data
            def read(self): return self._data
        read_headers, read_rows = import_from_excel(FakeFile(content))
        self.assertEqual(len(read_rows), 0)


class TestExportRoutes(unittest.TestCase):
    """测试各模块导出API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_products_export(self):
        resp = self.client.get('/products/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_suppliers_export(self):
        resp = self.client.get('/suppliers/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_customers_export(self):
        resp = self.client.get('/customers/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_purchase_export(self):
        resp = self.client.get('/purchase/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_sales_export(self):
        resp = self.client.get('/sales/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_inventory_export(self):
        resp = self.client.get('/inventory/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_finance_export(self):
        resp = self.client.get('/finance/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_products_template(self):
        resp = self.client.get('/products/api/template')
        self.assertEqual(resp.status_code, 200)


class TestImportRoutes(unittest.TestCase):
    """测试产品/供应商/客户导入API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM products WHERE name LIKE '导入测试商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '导入测试供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '导入测试客户_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '导入测试商品_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '导入测试供应商_%'")
        execute("DELETE FROM customers WHERE name LIKE '导入测试客户_%'")

    def _make_excel_file(self, headers, rows):
        content, _ = export_to_excel(headers, rows)
        return io.BytesIO(content)

    def test_products_import_add_new(self):
        """测试产品导入新增"""
        data = {
            'file': (self._make_excel_file(
                ['商品名称', '分类', '单位', '进货价', '售价', '预警值', '备注'],
                [['导入测试商品_新增', '测试分类', '个', '5', '10', '2', '测试备注']]
            ), 'test.xlsx')
        }
        resp = self.client.post('/products/api/import', data=data, content_type='multipart/form-data')
        result = resp.get_json()
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['added'], 1)

    def test_products_import_update_existing(self):
        """测试产品导入更新已存在"""
        # 先创建
        product_service.create_product({'name': '导入测试商品_更新', 'purchase_price': '5'})
        # 再导入更新
        data = {
            'file': (self._make_excel_file(
                ['商品名称', '分类', '单位', '进货价', '售价', '预警值', '备注'],
                [['导入测试商品_更新', '新分类', '箱', '8', '15', '5', '更新备注']]
            ), 'test.xlsx')
        }
        resp = self.client.post('/products/api/import', data=data, content_type='multipart/form-data')
        result = resp.get_json()
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['updated'], 1)

    def test_suppliers_import(self):
        """测试供应商导入"""
        data = {
            'file': (self._make_excel_file(
                ['供应商名称', '联系人', '电话', '地址', '备注'],
                [['导入测试供应商_1', '张三', '13800000000', '测试地址', '测试']]
            ), 'test.xlsx')
        }
        resp = self.client.post('/suppliers/api/import', data=data, content_type='multipart/form-data')
        result = resp.get_json()
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['added'], 1)

    def test_customers_import(self):
        """测试客户导入"""
        data = {
            'file': (self._make_excel_file(
                ['客户名称', '联系人', '电话', '地址', '备注'],
                [['导入测试客户_1', '李四', '13900000000', '测试地址', '测试']]
            ), 'test.xlsx')
        }
        resp = self.client.post('/customers/api/import', data=data, content_type='multipart/form-data')
        result = resp.get_json()
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['added'], 1)

    def test_import_no_file(self):
        """测试导入时未选择文件"""
        resp = self.client.post('/products/api/import', data={}, content_type='multipart/form-data')
        self.assertFalse(resp.get_json()['success'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
