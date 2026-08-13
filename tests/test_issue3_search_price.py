import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestIssue3SearchPurchasePrice(unittest.TestCase):
    """问题3：搜索结果显示产品进货价"""

    @classmethod
    def setUpClass(cls):
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        with open(cls.app_path, 'r', encoding='utf-8') as f:
            cls.app = f.read()

    def test_handle_search_function_exists(self):
        """测试handleSearch函数存在"""
        self.assertIn('function handleSearch', self.app)

    def test_search_shows_purchase_price(self):
        """测试搜索结果显示进货价"""
        # 在handleSearch函数中查找
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('进货价', search_section)

    def test_search_uses_purchase_price_field(self):
        """测试搜索结果使用purchase_price字段"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('p.purchase_price', search_section)

    def test_search_still_shows_sale_price(self):
        """测试搜索结果仍然显示售价"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('售价', search_section)
        self.assertIn('p.sale_price', search_section)

    def test_search_still_shows_stock(self):
        """测试搜索结果仍然显示库存"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('库存', search_section)
        self.assertIn('p.current_stock', search_section)

    def test_search_still_shows_brand_category(self):
        """测试搜索结果仍然显示品牌和分类"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('p.brand', search_section)
        self.assertIn('p.category', search_section)

    def test_search_still_shows_product_name(self):
        """测试搜索结果仍然显示产品名称"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('p.name', search_section)

    def test_search_still_has_low_stock_tag(self):
        """测试搜索结果仍然显示低库存标签"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('低库存', search_section)
        self.assertIn('isLow', search_section)

    def test_search_still_matches_product_name(self):
        """测试搜索仍然匹配产品名称"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn("p.name", search_section)
        self.assertIn("includes(keyword)", search_section)

    def test_search_still_has_empty_state(self):
        """测试搜索仍然有空状态"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('输入关键词搜索产品', search_section)
        self.assertIn('未找到相关产品', search_section)

    def test_search_uses_fmt_money_for_purchase_price(self):
        """测试进货价使用金额格式化"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        # 进货价那行应该有fmtMoney
        purchase_price_line = [line for line in search_section.split('\n') if '进货价' in line]
        self.assertTrue(len(purchase_price_line) > 0)
        self.assertIn('fmtMoney', purchase_price_line[0])

    def test_search_uses_fmt_money_for_sale_price(self):
        """测试售价使用金额格式化"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        sale_price_line = [line for line in search_section.split('\n') if '售价' in line]
        self.assertTrue(len(sale_price_line) > 0)
        self.assertIn('fmtMoney', sale_price_line[0])

    def test_search_still_has_list_item_class(self):
        """测试搜索结果仍然使用list-item样式"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('list-item', search_section)

    def test_search_still_has_item_meta_class(self):
        """测试搜索结果仍然使用item-meta样式"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('item-meta', search_section)

    def test_fmt_money_function_exists(self):
        """测试fmtMoney函数存在"""
        self.assertIn('function fmtMoney', self.app)

    def test_all_products_used_for_search(self):
        """测试搜索使用allProducts数据"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('allProducts', search_section)

    def test_search_input_id(self):
        """测试搜索框的ID是searchInput"""
        search_section = self.app.split('function handleSearch')[1].split('// ==================== 产品模块')[0]
        self.assertIn('searchInput', search_section)


if __name__ == '__main__':
    unittest.main(verbosity=2)
