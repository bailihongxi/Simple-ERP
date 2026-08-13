import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDeployment(unittest.TestCase):
    """测试部署相关配置（问题1：GitHub Pages部署）"""

    def test_root_index_html_exists(self):
        """测试根目录有index.html（GitHub Pages入口页）"""
        path = os.path.join(BASE_DIR, 'index.html')
        self.assertTrue(os.path.exists(path))

    def test_root_index_html_has_mobile_link(self):
        """测试根目录index.html有跳转到手机版的链接"""
        path = os.path.join(BASE_DIR, 'index.html')
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('mobile', html)
        self.assertIn('手机版', html)

    def test_mobile_index_html_exists(self):
        """测试mobile目录有index.html"""
        path = os.path.join(BASE_DIR, 'mobile', 'index.html')
        self.assertTrue(os.path.exists(path))

    def test_github_actions_workflow_exists(self):
        """测试GitHub Actions部署工作流存在"""
        path = os.path.join(BASE_DIR, '.github', 'workflows', 'deploy-pages.yml')
        self.assertTrue(os.path.exists(path))

    def test_workflow_has_deploy_steps(self):
        """测试工作流包含部署步骤"""
        path = os.path.join(BASE_DIR, '.github', 'workflows', 'deploy-pages.yml')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('actions/checkout', content)
        self.assertIn('actions/configure-pages', content)
        self.assertIn('actions/upload-pages-artifact', content)
        self.assertIn('actions/deploy-pages', content)

    def test_workflow_triggers_on_push(self):
        """测试工作流在push时触发"""
        path = os.path.join(BASE_DIR, '.github', 'workflows', 'deploy-pages.yml')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('push', content)
        self.assertIn('main', content)

    def test_workflow_has_permissions(self):
        """测试工作流有正确的权限配置"""
        path = os.path.join(BASE_DIR, '.github', 'workflows', 'deploy-pages.yml')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('pages: write', content)
        self.assertIn('id-token: write', content)

    def test_mobile_manifest_exists(self):
        """测试手机版manifest.json存在（PWA必需）"""
        path = os.path.join(BASE_DIR, 'mobile', 'manifest.json')
        self.assertTrue(os.path.exists(path))

    def test_mobile_sw_exists(self):
        """测试手机版service worker存在（PWA必需）"""
        path = os.path.join(BASE_DIR, 'mobile', 'sw.js')
        self.assertTrue(os.path.exists(path))

    def test_mobile_css_exists(self):
        """测试手机版CSS文件存在"""
        path = os.path.join(BASE_DIR, 'mobile', 'css', 'style.css')
        self.assertTrue(os.path.exists(path))

    def test_mobile_js_exists(self):
        """测试手机版JS文件存在"""
        path = os.path.join(BASE_DIR, 'mobile', 'js', 'app.js')
        self.assertTrue(os.path.exists(path))
        path2 = os.path.join(BASE_DIR, 'mobile', 'js', 'storage.js')
        self.assertTrue(os.path.exists(path2))


if __name__ == '__main__':
    unittest.main(verbosity=2)
