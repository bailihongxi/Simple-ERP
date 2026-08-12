from database.db import query_all, query_one, execute, get_db
from services import product_service


def recalc_avg_cost(product_id):
    """
    重新计算某商品的加权平均成本。
    按时间顺序遍历所有采购记录，逐次计算平均成本。
    只更新 avg_cost，不修改 current_stock。
    """
    purchases = query_all(
        "SELECT quantity, unit_price FROM purchases WHERE product_id = ? ORDER BY purchase_date, id",
        (product_id,)
    )
    stock = 0.0
    total_value = 0.0
    for p in purchases:
        total_value += p['quantity'] * p['unit_price']
        stock += p['quantity']
    avg_cost = total_value / stock if stock > 0 else 0
    execute("UPDATE products SET avg_cost = ? WHERE id = ?", (round(avg_cost, 4), product_id))
    return avg_cost


def get_purchases(date_start=None, date_end=None, supplier_id=None, keyword=None):
    """获取采购记录列表，支持筛选"""
    sql = """
        SELECT p.*, pr.name as product_name, s.name as supplier_name
        FROM purchases p
        LEFT JOIN products pr ON p.product_id = pr.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE 1=1
    """
    params = []
    if date_start:
        sql += " AND p.purchase_date >= ?"
        params.append(date_start)
    if date_end:
        sql += " AND p.purchase_date <= ?"
        params.append(date_end)
    if supplier_id:
        sql += " AND p.supplier_id = ?"
        params.append(supplier_id)
    if keyword:
        sql += " AND pr.name LIKE ?"
        params.append(f"%{keyword}%")
    sql += " ORDER BY p.purchase_date DESC, p.id DESC"
    return query_all(sql, params)


def get_purchase_by_id(purchase_id):
    """根据ID获取采购记录"""
    sql = """
        SELECT p.*, pr.name as product_name, s.name as supplier_name
        FROM purchases p
        LEFT JOIN products pr ON p.product_id = pr.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.id = ?
    """
    return query_one(sql, (purchase_id,))


def get_purchase_stats(date_start=None, date_end=None, supplier_id=None, keyword=None):
    """采购统计：总金额、笔数"""
    sql = "SELECT COALESCE(SUM(total_amount),0) as total_amount, COUNT(*) as count FROM purchases p LEFT JOIN products pr ON p.product_id = pr.id WHERE 1=1"
    params = []
    if date_start:
        sql += " AND p.purchase_date >= ?"
        params.append(date_start)
    if date_end:
        sql += " AND p.purchase_date <= ?"
        params.append(date_end)
    if supplier_id:
        sql += " AND p.supplier_id = ?"
        params.append(supplier_id)
    if keyword:
        sql += " AND pr.name LIKE ?"
        params.append(f"%{keyword}%")
    return query_one(sql, params)


def create_purchase(data):
    """
    创建采购记录：
    1. 插入采购记录
    2. 更新商品库存 current_stock += quantity
    3. 更新加权平均成本
    """
    product_id = int(data['product_id'])
    quantity = float(data['quantity'])
    unit_price = float(data['unit_price'])
    total_amount = round(quantity * unit_price, 2)
    purchase_date = data.get('purchase_date')
    supplier_id = data.get('supplier_id') or None
    payment_type = data.get('payment_type', 'cash')
    notes = data.get('notes', '')

    if quantity <= 0:
        raise ValueError('采购数量必须大于0')
    if unit_price < 0:
        raise ValueError('单价不能为负数')

    product = product_service.get_product_by_id(product_id)
    if not product:
        raise ValueError('产品不存在')

    old_stock = float(product['current_stock'])
    old_avg_cost = float(product['avg_cost'])

    # 计算新加权平均成本
    if old_stock + quantity > 0:
        new_avg_cost = (old_stock * old_avg_cost + quantity * unit_price) / (old_stock + quantity)
    else:
        new_avg_cost = 0

    conn = get_db()
    try:
        conn.execute('BEGIN')
        cursor = conn.execute(
            """INSERT INTO purchases (purchase_date, product_id, supplier_id, quantity, unit_price, total_amount, payment_type, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (purchase_date, product_id, supplier_id, quantity, unit_price, total_amount, payment_type, notes)
        )
        purchase_id = cursor.lastrowid
        conn.execute(
            "UPDATE products SET current_stock = current_stock + ?, avg_cost = ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (quantity, round(new_avg_cost, 4), product_id)
        )
        conn.execute('COMMIT')
        return purchase_id
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()


def update_purchase(purchase_id, data):
    """
    更新采购记录：
    1. 调整库存（新旧数量差）
    2. 更新采购记录
    3. 重算加权平均成本
    """
    old = get_purchase_by_id(purchase_id)
    if not old:
        raise ValueError('采购记录不存在')

    product_id = int(data['product_id'])
    quantity = float(data['quantity'])
    unit_price = float(data['unit_price'])
    total_amount = round(quantity * unit_price, 2)

    if quantity <= 0:
        raise ValueError('采购数量必须大于0')
    if unit_price < 0:
        raise ValueError('单价不能为负数')

    old_quantity = float(old['quantity'])
    delta = quantity - old_quantity

    conn = get_db()
    try:
        conn.execute('BEGIN')
        conn.execute(
            """UPDATE purchases SET purchase_date=?, product_id=?, supplier_id=?, quantity=?, unit_price=?,
               total_amount=?, payment_type=?, notes=? WHERE id=?""",
            (data.get('purchase_date'), product_id, data.get('supplier_id') or None,
             quantity, unit_price, total_amount, data.get('payment_type', 'cash'),
             data.get('notes', ''), purchase_id)
        )
        # 调整库存
        conn.execute(
            "UPDATE products SET current_stock = current_stock + ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (delta, product_id)
        )
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()

    # 重算加权平均成本
    recalc_avg_cost(product_id)


def delete_purchase(purchase_id):
    """
    删除采购记录：
    1. 回退库存 current_stock -= quantity
    2. 删除记录
    3. 重算加权平均成本
    """
    record = get_purchase_by_id(purchase_id)
    if not record:
        raise ValueError('采购记录不存在')

    product_id = record['product_id']
    quantity = float(record['quantity'])

    conn = get_db()
    try:
        conn.execute('BEGIN')
        conn.execute(
            "UPDATE products SET current_stock = current_stock - ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (quantity, product_id)
        )
        conn.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()

    # 重算加权平均成本
    recalc_avg_cost(product_id)


def batch_delete_purchases(purchase_ids):
    """
    批量删除采购记录：
    1. 遍历所有记录，回退库存
    2. 删除所有记录
    3. 对涉及的商品重算加权平均成本
    返回删除的记录数
    """
    if not purchase_ids:
        return 0

    # 获取所有要删除的记录
    placeholders = ','.join(['?'] * len(purchase_ids))
    records = query_all(
        f"SELECT id, product_id, quantity FROM purchases WHERE id IN ({placeholders})",
        purchase_ids
    )
    if not records:
        return 0

    # 收集涉及的商品ID
    product_ids = set(r['product_id'] for r in records)

    conn = get_db()
    try:
        conn.execute('BEGIN')
        for r in records:
            # 回退库存
            conn.execute(
                "UPDATE products SET current_stock = current_stock - ?, updated_at = datetime('now','localtime') WHERE id = ?",
                (float(r['quantity']), r['product_id'])
            )
            # 删除记录
            conn.execute("DELETE FROM purchases WHERE id = ?", (r['id'],))
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()

    # 对每个涉及的商品重算加权平均成本
    for pid in product_ids:
        recalc_avg_cost(pid)

    return len(records)
