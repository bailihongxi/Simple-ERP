import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobileHomePage(unittest.TestCase):
    """测试手机端首页（阶段3）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.css_path = os.path.join(MOBILE_DIR, 'css', 'style.css')

    def test_home_page_exists(self):
        """测试首页页面容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-home', html)

    def test_search_box_exists(self):
        """测试首页有搜索框"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('search-section', html)
        self.assertIn('search-box', html)
        self.assertIn('searchInput', html)

    def test_search_placeholder(self):
        """测试搜索框有占位文字"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('搜索商品名称', html)

    def test_search_icon_exists(self):
        """测试搜索框有搜索图标"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('search-icon', html)

    def test_handle_search_function_exists(self):
        """测试有handleSearch函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function handleSearch', code)

    def test_search_searches_products_only(self):
        """测试搜索只匹配产品名称"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('allProducts.filter', code)
        self.assertIn("p.name", code)
        self.assertIn("toLowerCase()", code)

    def test_search_results_container_exists(self):
        """测试搜索结果容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('searchResults', html)

    def test_search_empty_state(self):
        """测试搜索前有空状态提示"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('输入关键词搜索产品', html)

    def test_quick_section_exists(self):
        """测试首页有快捷入口区域"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('quick-section', html)
        self.assertIn('quick-grid', html)

    def test_four_quick_items(self):
        """测试有4个快捷入口"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        # 4个快捷入口：产品信息、库存查询、采购记录、销售记录
        self.assertIn('产品信息', html)
        self.assertIn('库存查询', html)
        self.assertIn('采购记录', html)
        self.assertIn('销售记录', html)
        # 统计quick-item数量
        count = html.count('quick-item')
        self.assertEqual(count, 4)

    def test_quick_item_icons(self):
        """测试快捷入口有图标"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('quick-icon', html)

    def test_quick_item_text(self):
        """测试快捷入口有文字"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('quick-text', html)

    def test_quick_item_go_to_products(self):
        """测试产品信息快捷入口跳转到产品页"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn("switchTab('products')", html)

    def test_quick_item_go_to_inventory(self):
        """测试库存查询快捷入口跳转到库存页"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('goToInventory()', html)

    def test_quick_item_go_to_purchase(self):
        """测试采购记录快捷入口跳转到采购页"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('goToPurchase()', html)

    def test_quick_item_go_to_sales(self):
        """测试销售记录快捷入口跳转到销售页"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn("switchTab('sales')", html)

    def test_load_home_data_function(self):
        """测试有loadHomeData函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function loadHomeData', code)

    def test_home_loads_products(self):
        """测试首页加载产品数据用于搜索"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn("getData('products')", code)
        self.assertIn('allProducts =', code)

    def test_search_result_shows_product_info(self):
        """测试搜索结果显示产品信息"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.name', code)
        self.assertIn('p.brand', code)
        self.assertIn('p.category', code)
        self.assertIn('p.current_stock', code)
        self.assertIn('p.sale_price', code)

    def test_search_result_shows_low_stock(self):
        """测试搜索结果显示低库存标识"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('isLow', code)
        self.assertIn('low-stock', code)
        self.assertIn('低库存', code)

    def test_search_section_style_exists(self):
        """测试搜索区域样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.search-section', css)
        self.assertIn('.search-box', css)

    def test_quick_section_style_exists(self):
        """测试快捷入口样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.quick-section', css)
        self.assertIn('.quick-grid', css)
        self.assertIn('.quick-item', css)

    def test_search_results_style_exists(self):
        """测试搜索结果样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.search-results', css)

    def test_search_no_results_state(self):
        """测试搜索无结果时有提示"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('未找到相关产品', code)


if __name__ == '__main__':
    unittest.main(verbosity=2)
