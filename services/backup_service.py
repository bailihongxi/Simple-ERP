import os
import shutil
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'erp_data.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')


def ensure_backup_dir():
    """确保备份目录存在"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


def create_backup():
    """
    创建数据库备份
    返回备份文件路径
    """
    ensure_backup_dir()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'backup_{timestamp}.db'
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def list_backups():
    """
    列出所有备份文件
    返回列表，每项含 filename, path, size, created_at
    """
    ensure_backup_dir()
    backups = []
    for filename in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if filename.endswith('.db'):
            filepath = os.path.join(BACKUP_DIR, filename)
            stat = os.stat(filepath)
            backups.append({
                'filename': filename,
                'path': filepath,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / 1024 / 1024, 2),
                'created_at': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    return backups


def restore_backup(filename):
    """
    从备份恢复数据库
    恢复前先自动备份当前数据到 backup_before_restore_时间戳.db
    """
    ensure_backup_dir()
    backup_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f'备份文件不存在：{filename}')

    # 恢复前自动备份当前数据
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    before_restore_path = os.path.join(BACKUP_DIR, f'backup_before_restore_{timestamp}.db')
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, before_restore_path)

    # 覆盖恢复
    shutil.copy2(backup_path, DB_PATH)
    return before_restore_path


def delete_backup(filename):
    """删除备份文件"""
    backup_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f'备份文件不存在：{filename}')
    os.remove(backup_path)
    return True
