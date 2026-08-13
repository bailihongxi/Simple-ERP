import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_DIR = os.path.join(BASE_DIR, 'mobile')


class TestMobileStorage(unittest.TestCase):
    """测试手机端数据存储与导入功能（阶段1）"""

    @classmethod
    def setUpClass(cls):
        cls.storage_path = os.path.join(MOBILE_DIR, 'js', 'storage.js')
        cls.app_path = os.path.join(MOBILE_DIR, 'js', 'app.js')
        cls.html_path = os.path.join(MOBILE_DIR, 'index.html')

    def test_storage_file_exists(self):
        """测试storage.js文件存在"""
        self.assertTrue(os.path.exists(self.storage_path))

    def test_storage_has_init_function(self):
        """测试有initStorage函数"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('initStorage', code)

    def test_storage_has_save_data(self):
        """测试有saveData函数"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('saveData', code)

    def test_storage_has_get_data(self):
        """测试有getData函数"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('getData', code)

    def test_storage_has_clear_all(self):
        """测试有clearAllData函数"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('clearAllData', code)

    def test_storage_has_meta_functions(self):
        """测试有setMeta和getMeta函数"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('setMeta', code)
        self.assertIn('getMeta', code)

    def test_storage_has_import_function(self):
        """测试有importData函数"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('importData', code)

    def test_import_validates_required_fields(self):
        """测试导入函数校验必要字段"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('products', code)
        self.assertIn('purchases', code)
        self.assertIn('sales', code)
        self.assertIn('数据格式不正确', code)

    def test_import_clears_old_data(self):
        """测试导入前清除旧数据（全量覆盖）"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('clearAllData()', code)

    def test_import_saves_all_stores(self):
        """测试导入保存所有数据类型"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn("'products'", code)
        self.assertIn("'purchases'", code)
        self.assertIn("'sales'", code)
        self.assertIn("'suppliers'", code)
        self.assertIn("'customers'", code)

    def test_import_saves_meta(self):
        """测试导入保存元数据（导入时间、版本）"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('export_time', code)
        self.assertIn('version', code)

    def test_app_has_import_handler(self):
        """测试app.js有导入处理函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('handleImport', code)
        self.assertIn('triggerImport', code)

    def test_import_has_confirmation(self):
        """测试导入前有确认弹窗"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('showConfirm', code)
        self.assertIn('确认导入', code)
        self.assertIn('覆盖现有全部数据', code)

    def test_app_has_clear_function(self):
        """测试app.js有清除数据函数"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('clearAllData', code)
        self.assertIn('确认清除', code)

    def test_app_has_data_summary(self):
        """测试app.js有数据概览功能"""
        with open(self.app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('loadMine', code)
        self.assertIn('dataSummary', code)

    def test_html_has_import_file_input(self):
        """测试HTML有文件导入input"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('importFile', html)
        self.assertIn('accept=".json"', html)

    def test_html_has_import_button(self):
        """测试HTML有导入按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('导入数据', html)

    def test_html_has_clear_button(self):
        """测试HTML有清除数据按钮"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('清除所有数据', html)

    def test_html_has_data_summary(self):
        """测试HTML有数据概览区域"""
        with open(self.html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('数据概览', html)
        self.assertIn('dataSummary', html)

    def test_storage_uses_localstorage(self):
        """测试存储使用localStorage"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('localStorage', code)
        self.assertIn('STORAGE_PREFIX', code)

    def test_storage_returns_promise(self):
        """测试存储函数返回Promise"""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            code = f.read()
        self.assertIn('new Promise', code)
        self.assertIn('resolve()', code)
        self.assertIn('reject', code)


if __name__ == '__main__':
    unittest.main(verbosity=2)
