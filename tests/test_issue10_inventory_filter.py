import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service, inventory_service
from database.db import execute


class TestInventoryBrandKeywordFilter(unittest.TestCase):
    """测试库存管理页面品牌和商品名称筛选（问题10）"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM products WHERE name LIKE '问题10_%'")
        cls.p1 = product_service.create_product({
            'name': '问题10_海尔冰箱', 'brand': '海尔', 'category': '冰箱',
            'purchase_price': '2000', 'sale_price': '2500'
        })
        cls.p2 = product_service.create_product({
            'name': '问题10_海尔洗衣机', 'brand': '海尔', 'category': '洗衣机',
            'purchase_price': '1500', 'sale_price': '2000'
        })
        cls.p3 = product_service.create_product({
            'name': '问题10_美的空调', 'brand': '美的', 'category': '空调',
            'purchase_price': '2500', 'sale_price': '3000'
        })
        execute("UPDATE products SET current_stock = 10, avg_cost = 100 WHERE id IN (?, ?, ?)",
                (cls.p1, cls.p2, cls.p3))

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '问题10_%'")

    def test_filter_by_brand(self):
        """测试按品牌筛选"""
        result = inventory_service.get_inventory_list(brand='海尔')
        names = [r['name'] for r in result]
        self.assertIn('问题10_海尔冰箱', names)
        self.assertIn('问题10_海尔洗衣机', names)
        self.assertNotIn('问题10_美的空调', names)

    def test_filter_by_keyword(self):
        """测试按商品名称关键词筛选"""
        result = inventory_service.get_inventory_list(keyword='冰箱')
        names = [r['name'] for r in result]
        self.assertIn('问题10_海尔冰箱', names)
        self.assertNotIn('问题10_海尔洗衣机', names)
        self.assertNotIn('问题10_美的空调', names)

    def test_filter_by_brand_and_keyword(self):
        """测试品牌+关键词组合筛选"""
        result = inventory_service.get_inventory_list(brand='海尔', keyword='洗衣机')
        names = [r['name'] for r in result]
        self.assertEqual(len(names), 1)
        self.assertIn('问题10_海尔洗衣机', names)

    def test_filter_by_category_brand_keyword(self):
        """测试分类+品牌+关键词组合筛选"""
        result = inventory_service.get_inventory_list(category='冰箱', brand='海尔', keyword='冰箱')
        names = [r['name'] for r in result]
        self.assertEqual(len(names), 1)
        self.assertIn('问题10_海尔冰箱', names)

    def test_no_filter_returns_all(self):
        """测试无筛选时返回全部"""
        result = inventory_service.get_inventory_list()
        names = [r['name'] for r in result]
        self.assertIn('问题10_海尔冰箱', names)
        self.assertIn('问题10_海尔洗衣机', names)
        self.assertIn('问题10_美的空调', names)

    def test_inventory_list_includes_brand_field(self):
        """测试库存列表返回brand字段"""
        result = inventory_service.get_inventory_list(keyword='问题10')
        for r in result:
            self.assertIn('brand', r)


class TestInventoryBrandKeywordRoutes(unittest.TestCase):
    """测试库存管理页面品牌和商品名称筛选路由（问题10）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_inventory_page_has_brand_filter(self):
        """测试库存页面包含品牌筛选下拉框"""
        resp = self.client.get('/inventory/')
        html = resp.get_data(as_text=True)
        self.assertIn('filterBrand', html)
        self.assertIn('全部品牌', html)

    def test_inventory_page_has_keyword_filter(self):
        """测试库存页面包含商品名称搜索框"""
        resp = self.client.get('/inventory/')
        html = resp.get_data(as_text=True)
        self.assertIn('filterKeyword', html)
        self.assertIn('搜索商品', html)

    def test_inventory_page_with_brand_param(self):
        """测试带品牌参数访问库存页面"""
        resp = self.client.get('/inventory/?brand=海尔')
        self.assertEqual(resp.status_code, 200)

    def test_inventory_page_with_keyword_param(self):
        """测试带关键词参数访问库存页面"""
        resp = self.client.get('/inventory/?keyword=冰箱')
        self.assertEqual(resp.status_code, 200)

    def test_inventory_page_with_all_params(self):
        """测试带所有筛选参数访问库存页面"""
        resp = self.client.get('/inventory/?keyword=冰箱&brand=海尔&category=冰箱&low_stock=')
        self.assertEqual(resp.status_code, 200)

    def test_inventory_export_includes_brand(self):
        """测试库存导出包含品牌列"""
        resp = self.client.get('/inventory/api/export')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('spreadsheet', resp.content_type)

    def test_inventory_export_with_filters(self):
        """测试库存导出带筛选参数"""
        resp = self.client.get('/inventory/api/export?brand=海尔&keyword=冰箱')
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
