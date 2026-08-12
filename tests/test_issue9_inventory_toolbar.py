import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class TestInventoryToolbarLayout(unittest.TestCase):
    """测试库存管理页面工具栏重新排布（问题9）"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_inventory_page_renders(self):
        """测试库存页面正常渲染"""
        resp = self.client.get('/inventory/')
        self.assertEqual(resp.status_code, 200)

    def test_inventory_page_has_filter_bar(self):
        """测试库存页面包含筛选栏"""
        resp = self.client.get('/inventory/')
        html = resp.get_data(as_text=True)
        self.assertIn('filter-bar', html)

    def test_inventory_page_has_category_filter(self):
        """测试库存页面包含分类筛选"""
        resp = self.client.get('/inventory/')
        html = resp.get_data(as_text=True)
        self.assertIn('filterCategory', html)
        self.assertIn('全部分类', html)

    def test_inventory_page_has_low_stock_filter(self):
        """测试库存页面包含只看低库存筛选，且使用统一的checkbox-label样式"""
        resp = self.client.get('/inventory/')
        html = resp.get_data(as_text=True)
        self.assertIn('filterLowStock', html)
        self.assertIn('checkbox-label', html)
        self.assertIn('只看低库存', html)

    def test_inventory_page_has_filter_actions(self):
        """测试库存页面筛选按钮使用filter-actions容器，排布在右侧"""
        resp = self.client.get('/inventory/')
        html = resp.get_data(as_text=True)
        self.assertIn('filter-actions', html)
        self.assertIn('筛选', html)
        self.assertIn('重置', html)

    def test_inventory_page_no_inline_style_on_checkbox(self):
        """测试库存页面不再使用inline style排布复选框（旧的不整齐方式）"""
        resp = self.client.get('/inventory/')
        html = resp.get_data(as_text=True)
        # 旧的inline style应该被移除
        self.assertNotIn('display:flex;align-items:center;gap:6px', html)

    def test_css_has_checkbox_label_style(self):
        """测试CSS文件包含checkbox-label样式"""
        with open('/Users/ybf/Desktop/ERP/static/css/style.css', 'r') as f:
            css = f.read()
        self.assertIn('.checkbox-label', css)
        self.assertIn('.filter-actions', css)

    def test_inventory_low_stock_filter_works(self):
        """测试只看低库存筛选参数正常工作"""
        resp = self.client.get('/inventory/?low_stock=1')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        # 复选框应该被选中
        self.assertIn('checked', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
