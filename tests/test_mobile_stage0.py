import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobilePWAInit(unittest.TestCase):
    """测试手机版PWA项目初始化（阶段0）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        cls.manifest_path = os.path.join(MOBILE_DIR, 'manifest.json')
        cls.sw_path = os.path.join(MOBILE_DIR, 'sw.js')
        cls.css_path = os.path.join(MOBILE_DIR, 'css', 'style.css')
        cls.js_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.storage_path = os.path.join(MOBILE_DIR, 'js', 'storage.js')

    def test_html_file_exists(self):
        """测试HTML文件存在"""
        self.assertTrue(os.path.exists(self.html_path))

    def test_html_has_doctype(self):
        """测试HTML包含DOCTYPE声明"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('<!DOCTYPE html>', html)

    def test_html_has_viewport(self):
        """测试HTML包含移动端viewport设置"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('viewport', html)
        self.assertIn('width=device-width', html)

    def test_html_has_manifest_link(self):
        """测试HTML引入了manifest"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('manifest.json', html)
        self.assertIn('rel="manifest"', html)

    def test_html_has_service_worker_registration(self):
        """测试HTML注册了service worker"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('serviceWorker', html)
        self.assertIn('sw.js', html)

    def test_manifest_file_exists(self):
        """测试manifest.json文件存在"""
        self.assertTrue(os.path.exists(self.manifest_path))

    def test_manifest_is_valid_json(self):
        """测试manifest.json格式正确"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_manifest_has_required_fields(self):
        """测试manifest包含必要字段"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('name', data)
        self.assertIn('short_name', data)
        self.assertIn('start_url', data)
        self.assertIn('display', data)
        self.assertIn('icons', data)
        self.assertEqual(data['display'], 'standalone')

    def test_sw_file_exists(self):
        """测试service worker文件存在"""
        self.assertTrue(os.path.exists(self.sw_path))

    def test_sw_has_install_event(self):
        """测试service worker有install事件"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn('install', sw)
        self.assertIn('activate', sw)
        self.assertIn('fetch', sw)

    def test_css_file_exists(self):
        """测试CSS文件存在"""
        self.assertTrue(os.path.exists(self.css_path))

    def test_js_file_exists(self):
        """测试JS文件存在"""
        self.assertTrue(os.path.exists(self.js_path))
        self.assertTrue(os.path.exists(self.storage_path))

    def test_bottom_nav_has_three_tabs(self):
        """测试底部导航有3个Tab"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('tabbar', html)
        self.assertIn('首页', html)
        self.assertIn('产品', html)
        self.assertIn('销售', html)
        # 统计tab-item数量
        tab_count = html.count('tab-item')
        self.assertGreaterEqual(tab_count, 3)

    def test_topbar_exists(self):
        """测试顶部栏存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('topbar', html)
        self.assertIn('settings-btn', html)
        self.assertIn('back-btn', html)

    def test_page_containers_exist(self):
        """测试各页面容器存在"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('page-home', html)
        self.assertIn('page-products', html)
        self.assertIn('page-sales', html)
        self.assertIn('page-inventory', html)
        self.assertIn('page-purchase', html)
        self.assertIn('page-mine', html)


if __name__ == '__main__':
    unittest.main(verbosity=2)
