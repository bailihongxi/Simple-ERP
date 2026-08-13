import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobileMinePage(unittest.TestCase):
    """测试手机端我的/设置模块（阶段7）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.css_path = os.path.join(MOBILE_DIR, 'css', 'style.css')

    def test_mine_page_exists(self):
        """测试我的页面容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-mine', html)

    def test_data_summary_card(self):
        """测试数据概览卡片存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('数据概览', html)
        self.assertIn('dataSummary', html)

    def test_data_management_card(self):
        """测试数据管理卡片存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('数据管理', html)

    def test_import_button_exists(self):
        """测试导入数据按钮存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('导入数据', html)
        self.assertIn('triggerImport()', html)

    def test_clear_button_exists(self):
        """测试清除数据按钮存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('清除所有数据', html)
        self.assertIn('clearAllData()', html)

    def test_about_card(self):
        """测试关于卡片存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('关于', html)

    def test_about_version(self):
        """测试关于页面显示版本号"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('版本', html)
        self.assertIn('v1.0', html)

    def test_about_data_storage_note(self):
        """测试关于页面有数据存储说明"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('数据保存在手机浏览器本地', html)

    def test_about_privacy_note(self):
        """测试关于页面有隐私说明（数据不上传）"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('不会上传到任何服务器', html)

    def test_load_mine_function(self):
        """测试有loadMine函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function loadMine', code)

    def test_mine_loads_all_data(self):
        """测试我的页面加载所有数据"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn("getData('products')", code)
        self.assertIn("getData('purchases')", code)
        self.assertIn("getData('sales')", code)

    def test_mine_shows_product_count(self):
        """测试数据概览显示商品数量"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('products.length', code)

    def test_mine_shows_purchase_count(self):
        """测试数据概览显示采购数量"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('purchases.length', code)

    def test_mine_shows_sale_count(self):
        """测试数据概览显示销售数量"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('sales.length', code)

    def test_mine_shows_inventory_value(self):
        """测试数据概览显示库存总价值"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('totalValue', code)
        self.assertIn('库存总价值', code)

    def test_mine_shows_import_time(self):
        """测试数据概览显示导入时间"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('import_time', code)
        self.assertIn('数据导入时间', code)

    def test_mine_empty_state(self):
        """测试无数据时显示空状态"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('暂无数据，请先导入数据', code)

    def test_trigger_import_function(self):
        """测试有triggerImport函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function triggerImport', code)

    def test_handle_import_function(self):
        """测试有handleImport函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('async function handleImport', code)

    def test_import_checks_file_type(self):
        """测试导入检查文件类型"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('.json', code)
        self.assertIn('请选择 JSON 格式', code)

    def test_import_parses_json(self):
        """测试导入解析JSON"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('JSON.parse', code)

    def test_import_validates_required_fields(self):
        """测试导入校验必要字段"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('products', code)
        self.assertIn('purchases', code)
        self.assertIn('sales', code)
        self.assertIn('文件格式不正确', code)

    def test_import_shows_confirmation(self):
        """测试导入前显示确认弹窗"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('showConfirm', code)
        self.assertIn('确认导入', code)
        self.assertIn('覆盖现有全部数据', code)

    def test_import_calls_import_data(self):
        """测试导入调用importData函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('importData(data)', code)

    def test_import_success_toast(self):
        """测试导入成功显示提示"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('导入成功', code)

    def test_import_failure_toast(self):
        """测试导入失败显示提示"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('导入失败', code)

    def test_clear_data_has_confirmation(self):
        """测试清除数据有确认弹窗"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('确认清除', code)
        self.assertIn('不可恢复', code)

    def test_clear_data_calls_clear_all(self):
        """测试清除数据调用clearAllData"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('clearAllData()', code)

    def test_clear_data_success_toast(self):
        """测试清除成功显示提示"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('数据已清除', code)

    def test_go_to_settings_function(self):
        """测试有goToSettings函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('function goToSettings', code)

    def test_settings_button_on_home(self):
        """测试首页有设置按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('settings-btn', html)
        self.assertIn('goToSettings()', html)

    def test_summary_grid_style_exists(self):
        """测试数据概览网格样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.summary-grid', css)
        self.assertIn('.summary-item-value', css)
        self.assertIn('.summary-item-label', css)

    def test_summary_extra_style_exists(self):
        """测试数据概览额外信息样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.summary-extra', css)

    def test_card_style_exists(self):
        """测试卡片样式存在"""
        with open(self.css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('.card', css)
        self.assertIn('.card-title', css)


if __name__ == '__main__':
    unittest.main(verbosity=2)
