import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestIssue4IconOptimization(unittest.TestCase):
    """问题4：图标重新优化，颜色更鲜艳"""

    @classmethod
    def setUpClass(cls):
        cls.manifest_path = os.path.join(MOBILE_DIR, 'manifest.json')
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')
        with open(cls.manifest_path, 'r', encoding='utf-8') as f:
            cls.manifest = json.load(f)
        with open(cls.html_path, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    # ==================== manifest.json 图标相关 ====================
    def test_manifest_has_icons(self):
        """测试manifest有icons配置"""
        self.assertIn('icons', self.manifest)
        self.assertIsInstance(self.manifest['icons'], list)
        self.assertGreater(len(self.manifest['icons']), 0)

    def test_icon_192_exists(self):
        """测试有192x192图标"""
        icons = self.manifest['icons']
        has_192 = any('192' in icon.get('sizes', '') for icon in icons)
        self.assertTrue(has_192, '缺少192x192图标')

    def test_icon_512_exists(self):
        """测试有512x512图标"""
        icons = self.manifest['icons']
        has_512 = any('512' in icon.get('sizes', '') for icon in icons)
        self.assertTrue(has_512, '缺少512x512图标')

    def test_icon_is_svg(self):
        """测试图标是SVG格式"""
        icons = self.manifest['icons']
        for icon in icons:
            self.assertIn('image/svg+xml', icon['type'])
            self.assertTrue(icon['src'].startswith('data:image/svg+xml'))

    def test_icon_has_gradient(self):
        """测试图标使用了渐变色（更鲜艳）"""
        icons = self.manifest['icons']
        for icon in icons:
            self.assertIn('linearGradient', icon['src'], '图标没有使用渐变色')

    def test_icon_has_bright_colors(self):
        """测试图标使用了鲜艳的颜色（橙色/黄色系）"""
        icons = self.manifest['icons']
        for icon in icons:
            src = icon['src']
            # 检查是否有橙色/黄色等鲜艳颜色
            has_orange = 'ff6b35' in src or 'ff7' in src or 'ff8' in src or 'ff9' in src
            has_yellow = 'f7c948' in src or 'feca57' in src or 'ffd' in src
            self.assertTrue(has_orange or has_yellow, '图标颜色不够鲜艳')

    def test_icon_not_blue_anymore(self):
        """测试图标不再是原来的蓝色"""
        icons = self.manifest['icons']
        for icon in icons:
            src = icon['src']
            # 原来的蓝色是 #3b82f6
            self.assertNotIn('3b82f6', src, '图标还是原来的蓝色，没有更新')

    def test_icon_has_box_shape(self):
        """测试图标中有箱子形状（进销存主题）"""
        icons = self.manifest['icons']
        for icon in icons:
            src = icon['src']
            # SVG路径，画的是箱子
            self.assertIn('path', src, '图标没有箱子形状')

    def test_icon_has_maskable(self):
        """测试图标支持maskable（适配各种形状）"""
        icons = self.manifest['icons']
        for icon in icons:
            self.assertIn('maskable', icon['purpose'])

    # ==================== 主题色相关 ====================
    def test_theme_color_updated(self):
        """测试theme_color已更新为鲜艳颜色"""
        self.assertIn('theme_color', self.manifest)
        # 检查不是原来的蓝色
        self.assertNotEqual(self.manifest['theme_color'], '#3b82f6')
        # 检查是橙色系（鲜艳颜色）
        theme = self.manifest['theme_color'].lower()
        self.assertTrue(theme.startswith('#ff') or '6b35' in theme or 'f7c9' in theme,
                        '主题色不够鲜艳')

    def test_background_color_updated(self):
        """测试background_color已更新"""
        self.assertIn('background_color', self.manifest)
        self.assertNotEqual(self.manifest['background_color'], '#ffffff')

    def test_html_theme_color_updated(self):
        """测试HTML中的theme-color meta标签已更新"""
        self.assertIn('theme-color', self.html)
        # 检查不是原来的蓝色
        self.assertNotIn('content="#3b82f6"', self.html)

    # ==================== manifest 其他配置 ====================
    def test_manifest_has_name(self):
        """测试manifest有name"""
        self.assertIn('name', self.manifest)
        self.assertEqual(self.manifest['name'], '进销存')

    def test_manifest_has_short_name(self):
        """测试manifest有short_name"""
        self.assertIn('short_name', self.manifest)
        self.assertEqual(self.manifest['short_name'], '进销存')

    def test_manifest_has_start_url(self):
        """测试manifest有start_url"""
        self.assertIn('start_url', self.manifest)
        self.assertIn('index.html', self.manifest['start_url'])

    def test_manifest_display_standalone(self):
        """测试manifest display为standalone（独立应用模式）"""
        self.assertIn('display', self.manifest)
        self.assertEqual(self.manifest['display'], 'standalone')

    def test_manifest_has_orientation(self):
        """测试manifest有方向设置（竖屏）"""
        self.assertIn('orientation', self.manifest)
        self.assertEqual(self.manifest['orientation'], 'portrait')

    def test_manifest_has_description(self):
        """测试manifest有描述"""
        self.assertIn('description', self.manifest)


if __name__ == '__main__':
    unittest.main(verbosity=2)
