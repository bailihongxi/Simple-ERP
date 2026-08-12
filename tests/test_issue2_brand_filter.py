import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service
from database.db import execute


class TestProductBrandFilter(unittest.TestCase):
    """测试产品品牌筛选功能（问题2）"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM products WHERE name LIKE '问题2_%'")
        # 创建不同品牌的产品
        product_service.create_product({'name': '问题2_商品A', 'brand': '品牌甲', 'category': '分类1'})
        product_service.create_product({'name': '问题2_商品B', 'brand': '品牌乙', 'category': '分类1'})
        product_service.create_product({'name': '问题2_商品C', 'brand': '品牌甲', 'category': '分类2'})
        product_service.create_product({'name': '问题2_商品D', 'brand': '', 'category': '分类1'})

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '问题2_%'")

    def test_filter_by_brand(self):
        """测试按品牌筛选"""
        results = product_service.get_products(brand='品牌甲')
        names = [r['name'] for r in results]
        self.assertIn('问题2_商品A', names)
        self.assertIn('问题2_商品C', names)
        self.assertNotIn('问题2_商品B', names)
        self.assertNotIn('问题2_商品D', names)

    def test_filter_by_brand_yi(self):
        """测试按品牌乙筛选"""
        results = product_service.get_products(brand='品牌乙')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], '问题2_商品B')

    def test_filter_by_brand_and_category(self):
        """测试品牌和分类组合筛选"""
        results = product_service.get_products(brand='品牌甲', category='分类1')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], '问题2_商品A')

    def test_filter_by_keyword_and_brand(self):
        """测试关键词和品牌组合筛选"""
        results = product_service.get_products(keyword='问题2_商品', brand='品牌甲')
        self.assertEqual(len(results), 2)

    def test_get_brands(self):
        """测试获取所有品牌列表"""
        brands = product_service.get_brands()
        self.assertIn('品牌甲', brands)
        self.assertIn('品牌乙', brands)
        # 空品牌不应出现在列表中
        self.assertNotIn('', brands)

    def test_no_brand_filter_returns_all(self):
        """测试不指定品牌时返回所有"""
        results = product_service.get_products(keyword='问题2_')
        self.assertEqual(len(results), 4)


class TestProductBrandFilterRoutes(unittest.TestCase):
    """测试产品品牌筛选路由（问题2）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_products_page_has_brand_filter(self):
        """测试产品页面包含品牌筛选下拉框"""
        resp = self.client.get('/products/')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('filterBrand', html)
        self.assertIn('全部品牌', html)

    def test_products_page_with_brand_param(self):
        """测试带品牌参数访问产品页面"""
        resp = self.client.get('/products/?brand=测试品牌')
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
