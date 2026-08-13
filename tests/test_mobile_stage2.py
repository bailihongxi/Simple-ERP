import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobileNavigation(unittest.TestCase):
    """测试手机端底部导航与页面框架（阶段2）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.css_path = os.path.join(MOBILE_DIR, 'css', 'style.css')

    def test_bottom_navigation_exists(self):
        """测试底部导航存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('tabbar', html)

    def test_bottom_nav_has_three_tabs(self):
        """测试底部导航有3个Tab：首页、产品、销售"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('data-tab="home"', html)
        self.assertIn('data-tab="products"', html)
        self.assertIn('data-tab="sales"', html)

    def test_tab_icons_and_text(self):
        """测试每个Tab有图标和文字"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('tab-icon', html)
        self.assertIn('tab-text', html)
        self.assertIn('首页', html)
        self.assertIn('产品', html)
        self.assertIn('销售', html)

    def test_switch_tab_function_exists(self):
        """测试有switchTab函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function switchTab', code)

    def test_page_titles_defined(self):
        """测试页面标题定义存在"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('pageTitles', code)
        self.assertIn('home', code)
        self.assertIn('products', code)
        self.assertIn('sales', code)
        self.assertIn('inventory', code)
        self.assertIn('purchase', code)
        self.assertIn('mine', code)

    def test_topbar_exists(self):
        """测试顶部栏存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('topbar', html)
        self.assertIn('topbar-title', html)

    def test_home_has_settings_button(self):
        """测试首页有设置按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('settings-btn', html)
        self.assertIn('settings-icon', html)

    def test_settings_goes_to_mine(self):
        """测试设置按钮跳转到我的页面"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('goToSettings', code)
        self.assertIn("navigateTo('mine')", code)

    def test_back_button_exists(self):
        """测试返回按钮存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('back-btn', html)
        self.assertIn('back-icon', html)

    def test_go_back_function_exists(self):
        """测试有goBack函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function goBack', code)

    def test_page_history_exists(self):
        """测试页面历史记录功能"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('pageHistory', code)
        self.assertIn('pageHistory.push', code)
        self.assertIn('pageHistory.pop', code)

    def test_navigate_to_function_exists(self):
        """测试有navigateTo函数（二级页面跳转）"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function navigateTo', code)

    def test_six_page_containers(self):
        """测试有6个页面容器：首页、产品、销售、库存、采购、我的"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-home', html)
        self.assertIn('page-products', html)
        self.assertIn('page-sales', html)
        self.assertIn('page-inventory', html)
        self.assertIn('page-purchase', html)
        self.assertIn('page-mine', html)

    def test_toast_function_exists(self):
        """测试有Toast提示功能"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function showToast', code)

    def test_toast_html_exists(self):
        """测试Toast HTML元素存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('id="toast"', html)

    def test_confirm_dialog_exists(self):
        """测试确认弹窗功能存在"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function showConfirm', code)
        self.assertIn('function closeModal', code)

    def test_confirm_dialog_html_exists(self):
        """测试确认弹窗HTML存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('modal-overlay', html)
        self.assertIn('modal-title', html)
        self.assertIn('modal-body', html)
        self.assertIn('modal-footer', html)

    def test_empty_state_exists(self):
        """测试空状态组件存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.empty-state', css)

    def test_list_item_style_exists(self):
        """测试列表卡片样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.list-item', css)

    def test_card_style_exists(self):
        """测试卡片样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.card', css)

    def test_filter_bar_style_exists(self):
        """测试筛选栏样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.filter-bar', css)
        self.assertIn('.filter-row', css)

    def test_button_styles_exist(self):
        """测试按钮样式存在（primary/secondary/warning等）"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.btn', css)
        self.assertIn('.btn-primary', css)
        self.assertIn('.btn-secondary', css)
        self.assertIn('.btn-warning', css)

    def test_tag_styles_exist(self):
        """测试标签样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.tag', css)
        self.assertIn('.tag-green', css)
        self.assertIn('.tag-red', css)
        self.assertIn('.tag-orange', css)

    def test_load_page_data_function(self):
        """测试有loadPageData函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function loadPageData', code)

    def test_init_function_exists(self):
        """测试有初始化函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function init', code)

    def test_default_page_is_home(self):
        """测试默认显示首页"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        # 首页应该有active类
        self.assertIn('page-home', html)
        # 检查第一个tab是active
        self.assertIn('tab-item active', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
