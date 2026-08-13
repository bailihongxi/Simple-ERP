import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestIssue1HomepageOptimization(unittest.TestCase):
    """问题1：首页优化 - 只保留搜索框，采购记录移到我的页面"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        with open(cls.html_path, 'r', encoding='utf-8') as f:
            cls.html = f.read()
        with open(cls.app_path, 'r', encoding='utf-8') as f:
            cls.app = f.read()

    # ==================== 首页相关 ====================
    def test_home_has_search_box(self):
        """测试首页有搜索框"""
        self.assertIn('searchInput', self.html)
        self.assertIn('搜索商品名称', self.html)

    def test_home_has_search_results(self):
        """测试首页有搜索结果区域"""
        self.assertIn('searchResults', self.html)

    def test_home_no_quick_section(self):
        """测试首页没有快捷入口区域（已移除）"""
        self.assertNotIn('quick-section', self.html)

    def test_home_no_quick_grid(self):
        """测试首页没有快捷入口网格"""
        self.assertNotIn('quick-grid', self.html)

    def test_home_no_product_quick_entry(self):
        """测试首页没有产品信息快捷入口"""
        # 首页不应该有"产品信息"的快捷入口文字
        # 但产品页面可能有，所以我们只检查首页区域
        home_section = self.html.split('id="page-home"')[1].split('</section>')[0]
        self.assertNotIn('产品信息', home_section)

    def test_home_no_sales_quick_entry(self):
        """测试首页没有销售记录快捷入口"""
        home_section = self.html.split('id="page-home"')[1].split('</section>')[0]
        self.assertNotIn('销售记录', home_section)

    def test_home_no_purchase_quick_entry(self):
        """测试首页没有采购记录快捷入口"""
        home_section = self.html.split('id="page-home"')[1].split('</section>')[0]
        self.assertNotIn('采购记录', home_section)

    def test_home_no_inventory_quick_entry(self):
        """测试首页没有库存查询快捷入口"""
        home_section = self.html.split('id="page-home"')[1].split('</section>')[0]
        self.assertNotIn('库存查询', home_section)

    def test_search_function_still_exists(self):
        """测试搜索功能仍然存在"""
        self.assertIn('handleSearch', self.app)
        self.assertIn('function handleSearch', self.app)

    def test_search_matches_product_name(self):
        """测试搜索仍然匹配产品名称"""
        self.assertIn('p.name', self.app)

    # ==================== 我的页面相关 ====================
    def test_mine_page_exists(self):
        """测试我的页面存在"""
        self.assertIn('page-mine', self.html)

    def test_mine_has_quick_entry_card(self):
        """测试我的页面有快捷入口卡片"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('快捷入口', mine_section)

    def test_mine_has_purchase_entry(self):
        """测试我的页面有采购记录入口"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('采购记录', mine_section)

    def test_mine_purchase_entry_has_icon(self):
        """测试采购记录入口有图标"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('📥', mine_section)

    def test_mine_purchase_entry_goes_to_purchase(self):
        """测试点击采购记录入口跳转到采购页"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('goToPurchase()', mine_section)

    def test_go_to_purchase_function_exists(self):
        """测试goToPurchase函数存在"""
        self.assertIn('function goToPurchase', self.app)

    def test_mine_still_has_data_summary(self):
        """测试我的页面仍然有数据概览"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('数据概览', mine_section)

    def test_mine_still_has_data_management(self):
        """测试我的页面仍然有数据管理"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('数据管理', mine_section)

    def test_mine_still_has_import_button(self):
        """测试我的页面仍然有导入数据按钮"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('导入数据', mine_section)

    def test_mine_still_has_clear_button(self):
        """测试我的页面仍然有清除数据按钮"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('清除所有数据', mine_section)

    def test_mine_still_has_about(self):
        """测试我的页面仍然有关于"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('关于', mine_section)

    # ==================== 底部导航相关 ====================
    def test_bottom_nav_has_three_tabs(self):
        """测试底部导航仍然有3个Tab"""
        self.assertIn('data-tab="home"', self.html)
        self.assertIn('data-tab="products"', self.html)
        self.assertIn('data-tab="sales"', self.html)

    def test_bottom_nav_home_tab(self):
        """测试底部导航有首页Tab"""
        self.assertIn('首页', self.html)

    def test_bottom_nav_products_tab(self):
        """测试底部导航有产品Tab"""
        self.assertIn('产品', self.html)

    def test_bottom_nav_sales_tab(self):
        """测试底部导航有销售Tab"""
        self.assertIn('销售', self.html)

    # ==================== 产品页面相关 ====================
    def test_product_page_still_has_quick_cards(self):
        """测试产品页面仍然有顶部快捷卡片（库存和采购）"""
        product_section = self.html.split('id="page-products"')[1].split('</section>')[0]
        self.assertIn('product-quick-cards', product_section)
        self.assertIn('库存总价值', product_section)
        self.assertIn('采购总金额', product_section)


if __name__ == '__main__':
    unittest.main(verbosity=2)
