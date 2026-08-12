from database.db import query_all, query_one, execute, get_db
from services import product_service


def get_inventory_list(category=None, low_stock_only=False):
    """获取库存列表，含库存价值"""
    sql = """
        SELECT p.id, p.name, p.category, p.unit, p.current_stock, p.avg_cost,
               p.warning_stock, s.name as supplier_name
        FROM products p
        LEFT JOIN suppliers s ON p.default_supplier_id = s.id
        WHERE 1=1
    """
    params = []
    if category:
        sql += " AND p.category = ?"
        params.append(category)
    if low_stock_only:
        sql += " AND p.warning_stock > 0 AND p.current_stock <= p.warning_stock"
    sql += " ORDER BY p.id DESC"
    rows = query_all(sql, params)
    for r in rows:
        r['stock_value'] = round(float(r['current_stock']) * float(r['avg_cost']), 2)
        r['is_low'] = float(r['warning_stock']) > 0 and float(r['current_stock']) <= float(r['warning_stock'])
    return rows


def get_inventory_summary():
    """库存汇总：商品种类数、库存总数量、总价值、低库存数"""
    total_products = query_one("SELECT COUNT(*) as cnt FROM products")['cnt']
    total_stock = query_one("SELECT COALESCE(SUM(current_stock),0) as total FROM products")['total']
    total_value = query_one("SELECT COALESCE(SUM(current_stock * avg_cost),0) as total FROM products")['total']
    low_stock_count = query_one(
        "SELECT COUNT(*) as cnt FROM products WHERE warning_stock > 0 AND current_stock <= warning_stock"
    )['cnt']
    return {
        'total_products': total_products,
        'total_stock': round(total_stock, 2),
        'total_value': round(total_value, 2),
        'low_stock_count': low_stock_count
    }


def adjust_stock(product_id, new_stock, reason, notes='', adjust_date=None):
    """
    盘点调整库存：
    1. 查出当前库存
    2. 计算变动量
    3. 插入盘点记录
    4. 更新产品库存
    """
    from utils.helpers import today_str
    if adjust_date is None:
        adjust_date = today_str()

    product = product_service.get_product_by_id(product_id)
    if not product:
        raise ValueError('产品不存在')

    old_stock = float(product['current_stock'])
    new_stock = float(new_stock)
    if new_stock < 0:
        raise ValueError('库存不能为负数')

    change_amount = round(new_stock - old_stock, 2)

    conn = get_db()
    try:
        conn.execute('BEGIN')
        conn.execute(
            """INSERT INTO inventory_adjustments (product_id, adjust_date, old_stock, new_stock,
               change_amount, reason, notes) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (product_id, adjust_date, old_stock, new_stock, change_amount, reason, notes)
        )
        conn.execute(
            "UPDATE products SET current_stock = ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (new_stock, product_id)
        )
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()

    return change_amount


def get_inventory_logs(product_id=None, limit=100):
    """
    库存变动流水：UNION 采购(+)、销售(-)、盘点调整
    按时间倒序
    """
    sql = """
        SELECT * FROM (
            SELECT 'purchase' as type, purchase_date as log_date, id as ref_id,
                   product_id, quantity as change_amount,
                   '采购入库' as change_type, notes, created_at
            FROM purchases
            UNION ALL
            SELECT 'sale' as type, sale_date as log_date, id as ref_id,
                   product_id, -quantity as change_amount,
                   '销售出库' as change_type, notes, created_at
            FROM sales
            UNION ALL
            SELECT 'adjust' as type, adjust_date as log_date, id as ref_id,
                   product_id, change_amount,
                   '盘点调整' as change_type, notes, created_at
            FROM inventory_adjustments
        ) WHERE 1=1
    """
    params = []
    if product_id:
        sql += " AND product_id = ?"
        params.append(product_id)
    sql += " ORDER BY log_date DESC, created_at DESC LIMIT ?"
    params.append(limit)

    rows = query_all(sql, params)
    # 关联商品名称
    for r in rows:
        p = product_service.get_product_by_id(r['product_id'])
        r['product_name'] = p['name'] if p else '-'
    return rows
