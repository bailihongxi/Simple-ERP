import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobileProductsPage(unittest.TestCase):
    """测试手机端产品模块（阶段4）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.css_path = os.path.join(MOBILE_DIR, 'css', 'style.css')

    def test_products_page_exists(self):
        """测试产品页面容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-products', html)

    def test_product_quick_cards_exists(self):
        """测试产品页顶部有快捷入口卡片"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('product-quick-cards', html)

    def test_two_quick_cards(self):
        """测试有2个快捷入口卡片：库存、采购"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        count = html.count('quick-card')
        self.assertGreaterEqual(count, 2)
        self.assertIn('库存总价值', html)
        self.assertIn('采购总金额', html)

    def test_quick_card_click_go_to_inventory(self):
        """测试库存卡片点击跳转到库存页"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('goToInventory()', html)

    def test_quick_card_click_go_to_purchase(self):
        """测试采购卡片点击跳转到采购页"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('goToPurchase()', html)

    def test_quick_card_hint_text(self):
        """测试快捷卡片有提示文字（点击查看...）"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('点击查看库存', html)
        self.assertIn('点击查看采购', html)

    def test_product_filter_bar_exists(self):
        """测试产品页有筛选栏"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        # 产品页的筛选栏
        self.assertIn('productBrand', html)
        self.assertIn('productCategory', html)

    def test_product_brand_filter(self):
        """测试产品页有品牌筛选下拉"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('全部品牌', html)

    def test_product_category_filter(self):
        """测试产品页有分类筛选下拉"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('全部分类', html)

    def test_product_filter_buttons(self):
        """测试产品页有筛选和重置按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('filterProducts()', html)
        self.assertIn('resetProductFilter()', html)

    def test_product_list_container_exists(self):
        """测试产品列表容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('productList', html)

    def test_product_empty_state(self):
        """测试产品页有空状态"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('暂无产品数据', html)

    def test_load_products_function_exists(self):
        """测试有loadProducts函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function loadProducts', code)

    def test_products_sorted_by_id_desc(self):
        """测试产品按ID倒序排列"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('b.id - a.id', code)

    def test_populate_brand_category_function(self):
        """测试有填充品牌分类下拉的函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function populateBrandCategory', code)

    def test_render_products_function_exists(self):
        """测试有renderProducts函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function renderProducts', code)

    def test_product_card_shows_name(self):
        """测试产品卡片显示名称"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.name', code)

    def test_product_card_shows_brand_category(self):
        """测试产品卡片显示品牌和分类"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.brand', code)
        self.assertIn('p.category', code)

    def test_product_card_shows_prices(self):
        """测试产品卡片显示进货价和售价"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.purchase_price', code)
        self.assertIn('p.sale_price', code)

    def test_product_card_shows_stock(self):
        """测试产品卡片显示库存"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.current_stock', code)

    def test_product_card_shows_low_stock_tag(self):
        """测试产品卡片低库存时显示标签"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('isLow', code)
        self.assertIn('低库存', code)

    def test_filter_products_by_brand(self):
        """测试可以按品牌筛选产品"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.brand === brand', code)

    def test_filter_products_by_category(self):
        """测试可以按分类筛选产品"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.category === category', code)

    def test_reset_product_filter_function(self):
        """测试有重置筛选函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function resetProductFilter', code)

    def test_update_quick_cards_function(self):
        """测试有更新快捷入口卡片数据的函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('updateProductQuickCards', code)

    def test_quick_card_inv_value_calculation(self):
        """测试库存总价值计算正确"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('current_stock', code)
        self.assertIn('avg_cost', code)

    def test_quick_card_purchase_total_calculation(self):
        """测试采购总金额计算正确"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('total_amount', code)

    def test_product_quick_cards_style_exists(self):
        """测试产品快捷入口卡片样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.product-quick-cards', css)
        self.assertIn('.quick-card', css)


if __name__ == '__main__':
    unittest.main(verbosity=2)
