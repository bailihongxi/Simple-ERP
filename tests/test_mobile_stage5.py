import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobileInventoryPurchasePages(unittest.TestCase):
    """测试手机端库存与采购模块（阶段5）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.css_path = os.path.join(MOBILE_DIR, 'css', 'style.css')

    # ==================== 库存模块 ====================
    def test_inventory_page_exists(self):
        """测试库存页面容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-inventory', html)

    def test_inventory_stats_grid(self):
        """测试库存页有统计卡片网格"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('stats-grid', html)

    def test_inventory_four_stats(self):
        """测试库存页有4个统计卡片"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('商品种类', html)
        self.assertIn('库存总数量', html)
        self.assertIn('库存总价值', html)
        self.assertIn('低库存预警', html)

    def test_inventory_stats_ids(self):
        """测试库存统计元素ID存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('invTotalProducts', html)
        self.assertIn('invTotalStock', html)
        self.assertIn('invTotalValue', html)
        self.assertIn('invLowStock', html)

    def test_inventory_filter_bar(self):
        """测试库存页有筛选栏"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('invKeyword', html)
        self.assertIn('invBrand', html)
        self.assertIn('invCategory', html)
        self.assertIn('invLowOnly', html)

    def test_inventory_low_stock_checkbox(self):
        """测试库存页有只看低库存复选框"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('只看低库存', html)

    def test_inventory_filter_buttons(self):
        """测试库存页有筛选和重置按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('filterInventory()', html)
        self.assertIn('resetInventoryFilter()', html)

    def test_inventory_list_container(self):
        """测试库存列表容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('inventoryList', html)

    def test_inventory_empty_state(self):
        """测试库存页有空状态"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('暂无库存数据', html)

    def test_load_inventory_function(self):
        """测试有loadInventory函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function loadInventory', code)

    def test_inventory_stats_calculation(self):
        """测试库存统计计算逻辑"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('totalProducts', code)
        self.assertIn('totalStock', code)
        self.assertIn('totalValue', code)
        self.assertIn('lowStock', code)

    def test_inventory_list_shows_product_name(self):
        """测试库存列表显示产品名称"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.name', code)

    def test_inventory_list_shows_brand_category(self):
        """测试库存列表显示品牌和分类"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.brand', code)
        self.assertIn('p.category', code)

    def test_inventory_list_shows_stock_and_cost(self):
        """测试库存列表显示库存和平均成本"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.current_stock', code)
        self.assertIn('p.avg_cost', code)

    def test_inventory_list_shows_stock_value(self):
        """测试库存列表显示库存价值"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('stockValue', code)

    def test_inventory_list_shows_status_tag(self):
        """测试库存列表显示状态标签（正常/低库存）"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('正常', code)
        self.assertIn('低库存', code)

    def test_filter_inventory_by_keyword(self):
        """测试库存可以按名称搜索"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('invKeyword', code)

    def test_filter_inventory_by_brand(self):
        """测试库存可以按品牌筛选"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.brand === brand', code)

    def test_filter_inventory_by_category(self):
        """测试库存可以按分类筛选"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.category === category', code)

    def test_filter_inventory_low_only(self):
        """测试库存可以只看低库存"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('lowOnly', code)
        self.assertIn('warning_stock', code)

    def test_reset_inventory_filter(self):
        """测试有重置库存筛选函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function resetInventoryFilter', code)

    # ==================== 采购模块 ====================
    def test_purchase_page_exists(self):
        """测试采购页面容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-purchase', html)

    def test_purchase_two_stats(self):
        """测试采购页有2个统计卡片"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('采购笔数', html)
        self.assertIn('采购总金额', html)

    def test_purchase_stats_ids(self):
        """测试采购统计元素ID存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('purCount', html)
        self.assertIn('purTotal', html)

    def test_purchase_filter_bar(self):
        """测试采购页有筛选栏"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('purDateStart', html)
        self.assertIn('purDateEnd', html)
        self.assertIn('purKeyword', html)

    def test_purchase_date_filter(self):
        """测试采购页有日期范围筛选"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('type="date"', html)

    def test_purchase_filter_buttons(self):
        """测试采购页有筛选和重置按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('filterPurchases()', html)
        self.assertIn('resetPurchaseFilter()', html)

    def test_purchase_list_container(self):
        """测试采购列表容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('purchaseList', html)

    def test_purchase_empty_state(self):
        """测试采购页有空状态"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('暂无采购记录', html)

    def test_load_purchases_function(self):
        """测试有loadPurchases函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function loadPurchases', code)

    def test_purchases_sorted_by_date(self):
        """测试采购按日期倒序排列"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('purchase_date', code)
        self.assertIn('localeCompare', code)

    def test_purchase_list_shows_product_name(self):
        """测试采购列表显示商品名称"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.product_name', code)

    def test_purchase_list_shows_supplier(self):
        """测试采购列表显示供应商"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.supplier_name', code)

    def test_purchase_list_shows_date(self):
        """测试采购列表显示日期"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.purchase_date', code)

    def test_purchase_list_shows_quantity_price(self):
        """测试采购列表显示数量和单价"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.quantity', code)
        self.assertIn('p.unit_price', code)

    def test_purchase_list_shows_total_amount(self):
        """测试采购列表显示总金额"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('p.total_amount', code)

    def test_purchase_list_shows_payment_type(self):
        """测试采购列表显示付款方式标签"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('payment_type', code)
        self.assertIn('赊账', code)
        self.assertIn('现结', code)

    def test_filter_purchases_by_date(self):
        """测试采购可以按日期范围筛选"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('dateStart', code)
        self.assertIn('dateEnd', code)

    def test_filter_purchases_by_keyword(self):
        """测试采购可以按关键词搜索（商品/供应商）"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('product_name', code)
        self.assertIn('supplier_name', code)

    def test_reset_purchase_filter(self):
        """测试有重置采购筛选函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function resetPurchaseFilter', code)

    def test_go_to_inventory_function(self):
        """测试有goToInventory函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function goToInventory', code)

    def test_go_to_purchase_function(self):
        """测试有goToPurchase函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function goToPurchase', code)

    def test_inventory_page_has_back_button(self):
        """测试库存页有返回按钮（通过顶部栏）"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('inventory', code)
        self.assertIn('backBtn', code)

    def test_purchase_page_has_back_button(self):
        """测试采购页有返回按钮（通过顶部栏）"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('purchase', code)
        self.assertIn('backBtn', code)

    def test_stats_grid_style_exists(self):
        """测试统计卡片网格样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.stats-grid', css)
        self.assertIn('.stat-card', css)


if __name__ == '__main__':
    unittest.main(verbosity=2)
