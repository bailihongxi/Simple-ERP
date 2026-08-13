import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobilePWAConfig(unittest.TestCase):
    """测试手机端PWA配置与部署准备（阶段8）"""

    @classmethod
    def setUpClass(cls):
        cls.manifest_path = os.path.join(MOBILE_DIR, 'manifest.json')
        cls.sw_path = os.path.join(MOBILE_DIR, 'sw.js')
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')

    # ==================== manifest.json 配置 ====================
    def test_manifest_file_exists(self):
        """测试manifest.json文件存在"""
        self.assertTrue(os.path.exists(self.manifest_path))

    def test_manifest_is_valid_json(self):
        """测试manifest.json是有效的JSON"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_manifest_has_name(self):
        """测试manifest有name字段"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('name', data)
        self.assertEqual(data['name'], '进销存')

    def test_manifest_has_short_name(self):
        """测试manifest有short_name字段"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('short_name', data)
        self.assertEqual(data['short_name'], '进销存')

    def test_manifest_has_start_url(self):
        """测试manifest有start_url字段"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('start_url', data)
        self.assertIn('index.html', data['start_url'])

    def test_manifest_display_standalone(self):
        """测试manifest display为standalone（独立应用模式）"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('display', data)
        self.assertEqual(data['display'], 'standalone')

    def test_manifest_has_background_color(self):
        """测试manifest有背景色"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('background_color', data)
        self.assertEqual(data['background_color'], '#ffffff')

    def test_manifest_has_theme_color(self):
        """测试manifest有主题色"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('theme_color', data)
        self.assertEqual(data['theme_color'], '#3b82f6')

    def test_manifest_has_icons(self):
        """测试manifest有图标配置"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('icons', data)
        self.assertIsInstance(data['icons'], list)
        self.assertGreater(len(data['icons']), 0)

    def test_manifest_has_192_icon(self):
        """测试manifest有192x192图标（PWA必需）"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        icons = data.get('icons', [])
        has_192 = any('192' in icon.get('sizes', '') for icon in icons)
        self.assertTrue(has_192, '缺少192x192图标')

    def test_manifest_has_512_icon(self):
        """测试manifest有512x512图标（PWA必需）"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        icons = data.get('icons', [])
        has_512 = any('512' in icon.get('sizes', '') for icon in icons)
        self.assertTrue(has_512, '缺少512x512图标')

    def test_manifest_has_orientation(self):
        """测试manifest有方向设置（竖屏）"""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('orientation', data)
        self.assertEqual(data['orientation'], 'portrait')

    # ==================== Service Worker 配置 ====================
    def test_sw_file_exists(self):
        """测试service worker文件存在"""
        self.assertTrue(os.path.exists(self.sw_path))

    def test_sw_has_cache_name(self):
        """测试service worker有缓存名称"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn('CACHE_NAME', sw)

    def test_sw_has_install_event(self):
        """测试service worker有install事件"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn("addEventListener('install'", sw)

    def test_sw_has_activate_event(self):
        """测试service worker有activate事件"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn("addEventListener('activate'", sw)

    def test_sw_has_fetch_event(self):
        """测试service worker有fetch事件"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn("addEventListener('fetch'", sw)

    def test_sw_precaches_static_files(self):
        """测试service worker预缓存静态文件"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn('urlsToCache', sw)
        self.assertIn('index.html', sw)
        self.assertIn('style.css', sw)
        self.assertIn('app.js', sw)
        self.assertIn('storage.js', sw)

    def test_sw_cache_first_strategy(self):
        """测试service worker使用缓存优先策略"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn('caches.match', sw)
        self.assertIn('return response', sw)

    def test_sw_cleans_old_cache(self):
        """测试service worker激活时清理旧缓存"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn('caches.delete', sw)

    def test_sw_skip_waiting(self):
        """测试service worker安装后立即激活"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn('skipWaiting', sw)

    def test_sw_clients_claim(self):
        """测试service worker激活后立即控制页面"""
        with open(self.sw_path, 'r', encoding='utf-8') as f:
            sw = f.read()
        self.assertIn('clients.claim', sw)

    # ==================== HTML 中的 PWA 配置 ====================
    def test_html_links_manifest(self):
        """测试HTML中引入了manifest"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('rel="manifest"', html)
        self.assertIn('manifest.json', html)

    def test_html_registers_sw(self):
        """测试HTML中注册了service worker"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('serviceWorker.register', html)
        self.assertIn('sw.js', html)

    def test_html_has_theme_color_meta(self):
        """测试HTML中有主题色meta标签"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('theme-color', html)
        self.assertIn('#3b82f6', html)

    def test_html_has_apple_web_app_meta(self):
        """测试HTML中有iOS Web App meta标签（支持iOS添加到桌面）"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('apple-mobile-web-app-capable', html)
        self.assertIn('apple-mobile-web-app-title', html)
        self.assertIn('apple-mobile-web-app-status-bar-style', html)

    # ==================== 部署相关 ====================
    def test_all_static_files_exist(self):
        """测试所有静态文件都存在"""
        files = [
            'index.html',
            'manifest.json',
            'sw.js',
            'css/style.css',
            'js/app.js',
            'js/storage.js',
        ]
        for f in files:
            path = os.path.join(MOBILE_DIR, f)
            self.assertTrue(os.path.exists(path), f'文件不存在：{f}')

    def test_mobile_directory_structure(self):
        """测试mobile目录结构完整"""
        self.assertTrue(os.path.isdir(os.path.join(MOBILE_DIR, 'css')))
        self.assertTrue(os.path.isdir(os.path.join(MOBILE_DIR, 'js')))

    def test_prd_document_exists(self):
        """测试PRD文档存在"""
        prd_path = os.path.join(MOBILE_DIR, 'PRD.md')
        self.assertTrue(os.path.exists(prd_path))

    def test_dev_plan_document_exists(self):
        """测试开发计划文档存在"""
        plan_path = os.path.join(MOBILE_DIR, 'DEVELOPMENT_PLAN.md')
        self.assertTrue(os.path.exists(plan_path))


if __name__ == '__main__':
    unittest.main(verbosity=2)
