import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import backup_service
from database.db import execute, query_one


class TestBackupService(unittest.TestCase):
    """测试备份服务层"""

    @classmethod
    def setUpClass(cls):
        # 清理测试备份
        backup_dir = backup_service.BACKUP_DIR
        if os.path.exists(backup_dir):
            for f in os.listdir(backup_dir):
                if f.startswith('test_backup_') or f.startswith('backup_before_restore_'):
                    os.remove(os.path.join(backup_dir, f))

    @classmethod
    def tearDownClass(cls):
        backup_dir = backup_service.BACKUP_DIR
        if os.path.exists(backup_dir):
            for f in os.listdir(backup_dir):
                if f.startswith('test_backup_') or f.startswith('backup_before_restore_'):
                    os.remove(os.path.join(backup_dir, f))

    def test_create_backup(self):
        """测试创建备份"""
        path = backup_service.create_backup()
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        # 清理
        os.remove(path)

    def test_list_backups(self):
        """测试列出备份"""
        path = backup_service.create_backup()
        backups = backup_service.list_backups()
        self.assertTrue(len(backups) >= 1)
        # 验证字段
        for b in backups:
            self.assertIn('filename', b)
            self.assertIn('size', b)
            self.assertIn('created_at', b)
        os.remove(path)

    def test_restore_backup_creates_before_restore(self):
        """测试恢复前自动备份当前数据"""
        # 创建一个备份
        path = backup_service.create_backup()
        filename = os.path.basename(path)

        # 恢复
        before_path = backup_service.restore_backup(filename)
        self.assertTrue(os.path.exists(before_path))

        # 清理
        os.remove(path)
        if os.path.exists(before_path):
            os.remove(before_path)

    def test_restore_nonexistent_raises(self):
        """测试恢复不存在的备份抛出异常"""
        with self.assertRaises(FileNotFoundError):
            backup_service.restore_backup('nonexistent_backup.db')

    def test_delete_backup(self):
        """测试删除备份"""
        path = backup_service.create_backup()
        filename = os.path.basename(path)
        backup_service.delete_backup(filename)
        self.assertFalse(os.path.exists(path))

    def test_delete_nonexistent_raises(self):
        """测试删除不存在的备份抛出异常"""
        with self.assertRaises(FileNotFoundError):
            backup_service.delete_backup('nonexistent_backup.db')


class TestBackupRoutes(unittest.TestCase):
    """测试备份路由API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        backup_dir = backup_service.BACKUP_DIR
        if os.path.exists(backup_dir):
            for f in os.listdir(backup_dir):
                if f.startswith('backup_') or f.startswith('backup_before_restore_'):
                    try:
                        os.remove(os.path.join(backup_dir, f))
                    except Exception:
                        pass

    def test_backup_page_renders(self):
        resp = self.client.get('/backup/')
        self.assertEqual(resp.status_code, 200)

    def test_create_backup_api(self):
        resp = self.client.post('/backup/api/create')
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('path', data)
        # 清理
        if os.path.exists(data['path']):
            os.remove(data['path'])

    def test_delete_backup_api(self):
        # 先创建
        path = backup_service.create_backup()
        filename = os.path.basename(path)
        # 删除
        resp = self.client.post('/backup/api/delete', data={'filename': filename})
        self.assertTrue(resp.get_json()['success'])
        self.assertFalse(os.path.exists(path))

    def test_delete_backup_api_no_filename(self):
        resp = self.client.post('/backup/api/delete', data={})
        self.assertFalse(resp.get_json()['success'])

    def test_restore_backup_api(self):
        # 先创建备份
        path = backup_service.create_backup()
        filename = os.path.basename(path)
        # 恢复
        resp = self.client.post('/backup/api/restore', data={'filename': filename})
        data = resp.get_json()
        self.assertTrue(data['success'])
        # 清理
        if os.path.exists(path):
            os.remove(path)
        if 'before_restore_path' in data and os.path.exists(data['before_restore_path']):
            os.remove(data['before_restore_path'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
