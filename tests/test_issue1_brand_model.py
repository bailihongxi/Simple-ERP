import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service
from database.db import execute, query_one, init_db


class TestProductBrandModel(unittest.TestCase):
    """测试产品品牌和型号字段（问题1）"""

    @classmethod
    def setUpClass(cls):
        init_db()  # 确保迁移执行
        execute("DELETE FROM products WHERE name LIKE '问题1_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '问题1_%'")

    def test_database_has_brand_model_columns(self):
        """测试数据库products表包含brand和model字段"""
        columns = query_one("PRAGMA table_info(products)")
        # PRAGMA返回多行，用query_all检查
        from database.db import query_all
        cols = query_all("PRAGMA table_info(products)")
        col_names = [c['name'] for c in cols]
        self.assertIn('brand', col_names)
        self.assertIn('model', col_names)

    def test_create_product_with_brand_model(self):
        """测试创建产品时品牌和型号被保存"""
        pid = product_service.create_product({
            'name': '问题1_测试商品',
            'brand': '测试品牌',
            'model': 'X100',
            'category': '测试分类',
            'purchase_price': '10',
            'sale_price': '20'
        })
        product = product_service.get_product_by_id(pid)
        self.assertEqual(product['brand'], '测试品牌')
        self.assertEqual(product['model'], 'X100')

    def test_update_product_brand_model(self):
        """测试更新产品时品牌和型号被更新"""
        pid = product_service.create_product({
            'name': '问题1_更新测试商品',
            'brand': '旧品牌',
            'model': '旧型号'
        })
        product_service.update_product(pid, {
            'name': '问题1_更新测试商品',
            'brand': '新品牌',
            'model': '新型号',
            'purchase_price': '10',
            'sale_price': '20'
        })
        product = product_service.get_product_by_id(pid)
        self.assertEqual(product['brand'], '新品牌')
        self.assertEqual(product['model'], '新型号')

    def test_product_list_includes_brand_model(self):
        """测试产品列表包含品牌和型号字段"""
        product_service.create_product({
            'name': '问题1_列表测试商品',
            'brand': '列表品牌',
            'model': 'L200'
        })
        products = product_service.get_products(keyword='问题1_列表测试商品')
        self.assertTrue(len(products) >= 1)
        self.assertIn('brand', products[0])
        self.assertIn('model', products[0])

    def test_create_product_empty_brand_model(self):
        """测试创建产品时品牌和型号为空也正常"""
        pid = product_service.create_product({
            'name': '问题1_空字段测试商品',
            'purchase_price': '5',
            'sale_price': '10'
        })
        product = product_service.get_product_by_id(pid)
        self.assertEqual(product['brand'], '')
        self.assertEqual(product['model'], '')


class TestProductBrandModelRoutes(unittest.TestCase):
    """测试产品品牌型号路由（问题1）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM products WHERE name LIKE '问题1路由_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '问题1路由_%'")

    def test_create_api_with_brand_model(self):
        resp = self.client.post('/products/api/create', data={
            'name': '问题1路由_测试商品',
            'brand': 'API品牌',
            'model': 'API-001',
            'purchase_price': '10',
            'sale_price': '20'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])
        product = product_service.get_product_by_id(data['id'])
        self.assertEqual(product['brand'], 'API品牌')
        self.assertEqual(product['model'], 'API-001')

    def test_products_page_renders(self):
        resp = self.client.get('/products/')
        self.assertEqual(resp.status_code, 200)
        # 页面应包含品牌和型号表头
        self.assertIn('品牌', resp.get_data(as_text=True))
        self.assertIn('型号', resp.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
