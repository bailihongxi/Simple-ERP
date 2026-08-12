import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service, supplier_service, purchase_service
from database.db import execute


class TestPurchaseSearchableDropdown(unittest.TestCase):
    """测试采购模块商品和供应商可搜索下拉（问题3）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM purchases WHERE notes LIKE '问题3_%'")
        execute("DELETE FROM products WHERE name LIKE '问题3_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题3_%'")
        cls.product_id = product_service.create_product({
            'name': '问题3_搜索商品', 'purchase_price': '10', 'sale_price': '20'
        })
        cls.supplier_id = supplier_service.create_supplier({
            'name': '问题3_搜索供应商'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM purchases WHERE notes LIKE '问题3_%'")
        execute("DELETE FROM products WHERE name LIKE '问题3_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '问题3_%'")

    def test_purchase_page_has_searchable_inputs(self):
        """测试采购页面包含可搜索的商品和供应商输入框"""
        resp = self.client.get('/purchase/')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        # 验证包含搜索相关元素
        self.assertIn('productSearch', html)
        self.assertIn('supplierSearch', html)
        self.assertIn('productDatalist', html)
        self.assertIn('supplierDatalist', html)
        self.assertIn('productId', html)
        self.assertIn('supplierId', html)
        # 验证包含搜索提示文字
        self.assertIn('输入搜索', html)

    def test_purchase_page_has_search_functions(self):
        """测试采购页面包含搜索处理函数"""
        resp = self.client.get('/purchase/')
        html = resp.get_data(as_text=True)
        self.assertIn('onProductSearchInput', html)
        self.assertIn('onProductSearchChange', html)
        self.assertIn('onSupplierSearchInput', html)
        self.assertIn('onSupplierSearchChange', html)

    def test_purchase_create_api_still_works(self):
        """测试采购创建API仍然正常工作（用product_id提交）"""
        resp = self.client.post('/purchase/api/create', data={
            'purchase_date': '2026-08-12',
            'product_id': self.product_id,
            'supplier_id': self.supplier_id,
            'quantity': '5',
            'unit_price': '10',
            'payment_type': 'cash',
            'notes': '问题3_测试采购'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])

    def test_purchase_edit_api_still_works(self):
        """测试采购编辑API仍然正常工作"""
        # 先创建
        pid = purchase_service.create_purchase({
            'purchase_date': '2026-08-12',
            'product_id': self.product_id,
            'supplier_id': self.supplier_id,
            'quantity': '3',
            'unit_price': '8',
            'payment_type': 'cash',
            'notes': '问题3_编辑测试'
        })
        # 再编辑
        resp = self.client.post('/purchase/api/update/' + str(pid), data={
            'purchase_date': '2026-08-12',
            'product_id': self.product_id,
            'supplier_id': self.supplier_id,
            'quantity': '10',
            'unit_price': '12',
            'payment_type': 'credit',
            'notes': '问题3_编辑测试_已编辑'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])

    def test_purchase_new_action_auto_open(self):
        """测试?action=new参数页面正常渲染"""
        resp = self.client.get('/purchase/?action=new')
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
