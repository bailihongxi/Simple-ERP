import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestIssue2DataOverview(unittest.TestCase):
    """问题2：产品页面快捷卡片移到我的页面数据概览"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        with open(cls.html_path, 'r', encoding='utf-8') as f:
            cls.html = f.read()
        with open(cls.app_path, 'r', encoding='utf-8') as f:
            cls.app = f.read()

    # ==================== 产品页面相关 ====================
    def test_product_page_no_quick_cards(self):
        """测试产品页面没有顶部快捷卡片了"""
        product_section = self.html.split('id="page-products"')[1].split('</section>')[0]
        self.assertNotIn('product-quick-cards', product_section)

    def test_product_page_no_inv_value_card(self):
        """测试产品页面没有库存总价值卡片"""
        product_section = self.html.split('id="page-products"')[1].split('</section>')[0]
        self.assertNotIn('quickInvValue', product_section)

    def test_product_page_no_pur_total_card(self):
        """测试产品页面没有采购总金额卡片"""
        product_section = self.html.split('id="page-products"')[1].split('</section>')[0]
        self.assertNotIn('quickPurTotal', product_section)

    def test_product_page_starts_with_filter(self):
        """测试产品页面顶部直接是筛选栏"""
        product_section = self.html.split('id="page-products"')[1].split('</section>')[0]
        # 筛选栏应该在比较靠前的位置
        filter_pos = product_section.find('filter-bar')
        self.assertGreater(filter_pos, 0)
        self.assertLess(filter_pos, 200)  # 在前200个字符内

    def test_product_page_still_has_filter(self):
        """测试产品页面仍然有筛选功能"""
        product_section = self.html.split('id="page-products"')[1].split('</section>')[0]
        self.assertIn('productBrand', product_section)
        self.assertIn('productCategory', product_section)
        self.assertIn('filterProducts', product_section)
        self.assertIn('resetProductFilter', product_section)

    def test_product_page_still_has_list(self):
        """测试产品页面仍然有产品列表"""
        product_section = self.html.split('id="page-products"')[1].split('</section>')[0]
        self.assertIn('productList', product_section)

    def test_no_update_quick_cards_function(self):
        """测试updateProductQuickCards函数已移除"""
        self.assertNotIn('function updateProductQuickCards', self.app)

    def test_load_products_no_calls_update(self):
        """测试loadProducts不再调用updateProductQuickCards"""
        self.assertNotIn('updateProductQuickCards()', self.app)

    # ==================== 我的页面数据概览 ====================
    def test_mine_data_summary_exists(self):
        """测试我的页面有数据概览"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('数据概览', mine_section)
        self.assertIn('dataSummary', mine_section)

    def test_load_mine_function_exists(self):
        """测试loadMine函数存在"""
        self.assertIn('function loadMine', self.app)

    def test_load_mine_loads_all_data(self):
        """测试loadMine加载所有数据"""
        self.assertIn("getData('products')", self.app)
        self.assertIn("getData('purchases')", self.app)
        self.assertIn("getData('sales')", self.app)

    def test_load_mine_calculates_inventory_value(self):
        """测试loadMine计算库存总价值"""
        self.assertIn('totalValue', self.app)
        self.assertIn('current_stock', self.app)
        self.assertIn('avg_cost', self.app)

    def test_load_mine_calculates_purchase_total(self):
        """测试loadMine计算采购总金额"""
        self.assertIn('purchaseTotal', self.app)
        self.assertIn('total_amount', self.app)

    def test_load_mine_shows_inventory_value(self):
        """测试数据概览显示库存总价值"""
        # 在loadMine函数中查找
        load_mine_section = self.app.split('async function loadMine')[1].split('function triggerImport')[0]
        self.assertIn('库存总价值', load_mine_section)

    def test_load_mine_shows_purchase_total(self):
        """测试数据概览显示采购总金额"""
        load_mine_section = self.app.split('async function loadMine')[1].split('function triggerImport')[0]
        self.assertIn('采购总金额', load_mine_section)

    def test_load_mine_shows_import_time(self):
        """测试数据概览显示导入时间"""
        load_mine_section = self.app.split('async function loadMine')[1].split('function triggerImport')[0]
        self.assertIn('数据导入时间', load_mine_section)

    def test_summary_grid_three_items(self):
        """测试数据概览有3个统计项（商品、采购、销售）"""
        load_mine_section = self.app.split('async function loadMine')[1].split('function triggerImport')[0]
        self.assertIn('summary-grid', load_mine_section)
        self.assertIn('商品', load_mine_section)
        self.assertIn('采购', load_mine_section)
        self.assertIn('销售', load_mine_section)

    def test_summary_extra_exists(self):
        """测试数据概览有额外信息区域"""
        load_mine_section = self.app.split('async function loadMine')[1].split('function triggerImport')[0]
        self.assertIn('summary-extra', load_mine_section)

    # ==================== 其他验证 ====================
    def test_go_to_inventory_still_exists(self):
        """测试goToInventory函数仍然存在"""
        self.assertIn('function goToInventory', self.app)

    def test_go_to_purchase_still_exists(self):
        """测试goToPurchase函数仍然存在"""
        self.assertIn('function goToPurchase', self.app)

    def test_inventory_page_still_exists(self):
        """测试库存页面仍然存在"""
        self.assertIn('page-inventory', self.html)

    def test_purchase_page_still_exists(self):
        """测试采购页面仍然存在"""
        self.assertIn('page-purchase', self.html)

    def test_mine_still_has_purchase_entry(self):
        """测试我的页面仍然有采购记录快捷入口"""
        mine_section = self.html.split('id="page-mine"')[1].split('</section>')[0]
        self.assertIn('采购记录', mine_section)


if __name__ == '__main__':
    unittest.main(verbosity=2)
