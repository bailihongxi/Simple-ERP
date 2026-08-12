import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'erp_data.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')


def get_db():
    """获取数据库连接，每次调用创建新连接（Flask请求范围内使用）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """初始化数据库，创建表结构，并处理字段迁移"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    # 迁移：为已有products表添加brand和model字段
    cursor = conn.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'brand' not in columns:
        conn.execute("ALTER TABLE products ADD COLUMN brand TEXT DEFAULT ''")
    if 'model' not in columns:
        conn.execute("ALTER TABLE products ADD COLUMN model TEXT DEFAULT ''")

    conn.commit()
    conn.close()


def query_all(sql, params=()):
    """查询所有记录"""
    conn = get_db()
    try:
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def query_one(sql, params=()):
    """查询单条记录"""
    conn = get_db()
    try:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def execute(sql, params=()):
    """执行写入操作，返回最后插入的ID"""
    conn = get_db()
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def execute_transaction(operations):
    """
    执行事务，operations为列表，每个元素为 (sql, params) 元组
    返回事务中最后插入的ID
    """
    conn = get_db()
    last_id = None
    try:
        conn.execute('BEGIN')
        for sql, params in operations:
            cursor = conn.execute(sql, params)
            if cursor.lastrowid:
                last_id = cursor.lastrowid
        conn.execute('COMMIT')
        return last_id
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()
