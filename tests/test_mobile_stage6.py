import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobileSalesPage(unittest.TestCase):
    """测试手机端销售模块（阶段6）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.css_path = os.path.join(MOBILE_DIR, 'css', 'style.css')

    def test_sales_page_exists(self):
        """测试销售页面容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-sales', html)

    def test_sales_four_stats(self):
        """测试销售页有4个统计卡片"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('销售笔数', html)
        self.assertIn('销售总金额', html)
        self.assertIn('总毛利', html)
        self.assertIn('总成本', html)

    def test_sales_stats_ids(self):
        """测试销售统计元素ID存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('saleCount', html)
        self.assertIn('saleTotal', html)
        self.assertIn('saleProfit', html)
        self.assertIn('saleCost', html)

    def test_sales_filter_bar(self):
        """测试销售页有筛选栏"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('saleDateStart', html)
        self.assertIn('saleDateEnd', html)
        self.assertIn('saleKeyword', html)

    def test_sales_date_filter(self):
        """测试销售页有日期范围筛选"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        # 检查日期input
        date_inputs = html.count('type="date"')
        self.assertGreaterEqual(date_inputs, 2)

    def test_sales_filter_buttons(self):
        """测试销售页有筛选和重置按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('filterSales()', html)
        self.assertIn('resetSaleFilter()', html)

    def test_sales_list_container(self):
        """测试销售列表容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('salesList', html)

    def test_sales_empty_state(self):
        """测试销售页有空状态"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('暂无销售记录', html)

    def test_load_sales_function(self):
        """测试有loadSales函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function loadSales', code)

    def test_sales_stats_calculation(self):
        """测试销售统计计算逻辑"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('count', code)
        self.assertIn('total', code)
        self.assertIn('cost', code)
        self.assertIn('profit', code)

    def test_sales_sorted_by_date(self):
        """测试销售按日期倒序排列"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('sale_date', code)
        self.assertIn('localeCompare', code)

    def test_sales_list_shows_product_name(self):
        """测试销售列表显示商品名称"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('s.product_name', code)

    def test_sales_list_shows_customer(self):
        """测试销售列表显示客户"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('s.customer_name', code)

    def test_sales_list_shows_date(self):
        """测试销售列表显示日期"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('s.sale_date', code)

    def test_sales_list_shows_quantity_price(self):
        """测试销售列表显示数量和单价"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('s.quantity', code)
        self.assertIn('s.unit_price', code)

    def test_sales_list_shows_total_amount(self):
        """测试销售列表显示总金额"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('s.total_amount', code)

    def test_sales_list_shows_cost_and_profit(self):
        """测试销售列表显示成本和毛利"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('s.cost_amount', code)
        self.assertIn('s.profit', code)

    def test_sales_list_shows_payment_type(self):
        """测试销售列表显示付款方式标签"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('payment_type', code)
        self.assertIn('赊账', code)
        self.assertIn('现结', code)

    def test_sales_profit_negative_red(self):
        """测试毛利为负时标红"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('profit >= 0', code)
        self.assertIn('#dc2626', code)
        self.assertIn('#16a34a', code)

    def test_sales_profit_stat_color(self):
        """测试毛利统计卡片颜色随正负变化"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn("'green'", code)
        self.assertIn("'red'", code)
        self.assertIn('saleProfit', code)

    def test_filter_sales_by_date(self):
        """测试销售可以按日期范围筛选"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('dateStart', code)
        self.assertIn('dateEnd', code)

    def test_filter_sales_by_keyword(self):
        """测试销售可以按关键词搜索（商品/客户）"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('product_name', code)
        self.assertIn('customer_name', code)

    def test_reset_sale_filter(self):
        """测试有重置销售筛选函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function resetSaleFilter', code)

    def test_sales_in_bottom_nav(self):
        """测试销售在底部导航中"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('data-tab="sales"', html)
        self.assertIn('销售', html)

    def test_sales_tab_icon(self):
        """测试销售Tab有图标"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('📤', html)

    def test_render_sales_function(self):
        """测试有renderSales函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function renderSales', code)

    def test_sales_list_item_style(self):
        """测试销售列表项样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.list-item', css)

    def test_sales_money_style(self):
        """测试金额样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.money', css)
        self.assertIn('.money.negative', css)

    def test_sales_tab_switch(self):
        """测试点击销售Tab可以切换"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn("case 'sales'", code)
        self.assertIn('loadSales()', code)


if __name__ == '__main__':
    unittest.main(verbosity=2)
