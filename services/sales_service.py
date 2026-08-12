from database.db import query_all, query_one, execute, get_db
from services import product_service


def get_sales(date_start=None, date_end=None, customer_id=None, keyword=None):
    """获取销售记录列表，支持筛选"""
    sql = """
        SELECT s.*, p.name as product_name, c.name as customer_name
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE 1=1
    """
    params = []
    if date_start:
        sql += " AND s.sale_date >= ?"
        params.append(date_start)
    if date_end:
        sql += " AND s.sale_date <= ?"
        params.append(date_end)
    if customer_id:
        sql += " AND s.customer_id = ?"
        params.append(customer_id)
    if keyword:
        sql += " AND p.name LIKE ?"
        params.append(f"%{keyword}%")
    sql += " ORDER BY s.sale_date DESC, s.id DESC"
    return query_all(sql, params)


def get_sale_by_id(sale_id):
    """根据ID获取销售记录"""
    sql = """
        SELECT s.*, p.name as product_name, c.name as customer_name
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE s.id = ?
    """
    return query_one(sql, (sale_id,))


def get_sales_stats(date_start=None, date_end=None, customer_id=None, keyword=None):
    """销售统计：总金额、总成本、总毛利、笔数"""
    sql = """
        SELECT COALESCE(SUM(total_amount),0) as total_amount,
               COALESCE(SUM(cost_amount),0) as total_cost,
               COALESCE(SUM(profit),0) as total_profit,
               COUNT(*) as count
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        WHERE 1=1
    """
    params = []
    if date_start:
        sql += " AND s.sale_date >= ?"
        params.append(date_start)
    if date_end:
        sql += " AND s.sale_date <= ?"
        params.append(date_end)
    if customer_id:
        sql += " AND s.customer_id = ?"
        params.append(customer_id)
    if keyword:
        sql += " AND p.name LIKE ?"
        params.append(f"%{keyword}%")
    return query_one(sql, params)


def create_sale(data):
    """
    创建销售记录：
    1. 检查库存是否充足
    2. 计算成本（当前加权平均成本 × 数量）
    3. 计算利润
    4. 插入记录 + 减少库存
    """
    product_id = int(data['product_id'])
    quantity = float(data['quantity'])
    unit_price = float(data['unit_price'])
    total_amount = round(quantity * unit_price, 2)
    sale_date = data.get('sale_date')
    customer_id = data.get('customer_id') or None
    payment_type = data.get('payment_type', 'cash')
    notes = data.get('notes', '')

    if quantity <= 0:
        raise ValueError('销售数量必须大于0')
    if unit_price < 0:
        raise ValueError('单价不能为负数')

    product = product_service.get_product_by_id(product_id)
    if not product:
        raise ValueError('产品不存在')

    current_stock = float(product['current_stock'])
    if quantity > current_stock:
        raise ValueError(f'库存不足！当前库存：{current_stock}，需要：{quantity}')

    avg_cost = float(product['avg_cost'])
    cost_amount = round(avg_cost * quantity, 2)
    profit = round(total_amount - cost_amount, 2)

    conn = get_db()
    try:
        conn.execute('BEGIN')
        cursor = conn.execute(
            """INSERT INTO sales (sale_date, product_id, customer_id, quantity, unit_price,
               total_amount, cost_amount, profit, payment_type, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sale_date, product_id, customer_id, quantity, unit_price,
             total_amount, cost_amount, profit, payment_type, notes)
        )
        sale_id = cursor.lastrowid
        conn.execute(
            "UPDATE products SET current_stock = current_stock - ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (quantity, product_id)
        )
        conn.execute('COMMIT')
        return sale_id
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()


def update_sale(sale_id, data):
    """
    更新销售记录：
    1. 调整库存（新旧数量差）
    2. 用当前加权平均成本重算本次销售的成本和利润
    3. 更新记录
    """
    old = get_sale_by_id(sale_id)
    if not old:
        raise ValueError('销售记录不存在')

    product_id = int(data['product_id'])
    quantity = float(data['quantity'])
    unit_price = float(data['unit_price'])
    total_amount = round(quantity * unit_price, 2)

    if quantity <= 0:
        raise ValueError('销售数量必须大于0')
    if unit_price < 0:
        raise ValueError('单价不能为负数')

    old_quantity = float(old['quantity'])
    delta = quantity - old_quantity

    product = product_service.get_product_by_id(product_id)
    if not product:
        raise ValueError('产品不存在')

    # 检查库存（如果增加销售数量，需要额外库存）
    if delta > 0:
        available = float(product['current_stock'])
        if delta > available:
            raise ValueError(f'库存不足！当前库存：{available}，还需：{delta}')

    # 用当前加权平均成本重算
    avg_cost = float(product['avg_cost'])
    cost_amount = round(avg_cost * quantity, 2)
    profit = round(total_amount - cost_amount, 2)

    conn = get_db()
    try:
        conn.execute('BEGIN')
        conn.execute(
            """UPDATE sales SET sale_date=?, product_id=?, customer_id=?, quantity=?, unit_price=?,
               total_amount=?, cost_amount=?, profit=?, payment_type=?, notes=? WHERE id=?""",
            (data.get('sale_date'), product_id, data.get('customer_id') or None,
             quantity, unit_price, total_amount, cost_amount, profit,
             data.get('payment_type', 'cash'), data.get('notes', ''), sale_id)
        )
        # 调整库存：delta>0表示销售增加，库存减少；delta<0表示销售减少，库存增加
        conn.execute(
            "UPDATE products SET current_stock = current_stock - ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (delta, product_id)
        )
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()


def delete_sale(sale_id):
    """
    删除销售记录：
    1. 回退库存
    2. 删除记录
    """
    record = get_sale_by_id(sale_id)
    if not record:
        raise ValueError('销售记录不存在')

    product_id = record['product_id']
    quantity = float(record['quantity'])

    conn = get_db()
    try:
        conn.execute('BEGIN')
        conn.execute(
            "UPDATE products SET current_stock = current_stock + ?, updated_at = datetime('now','localtime') WHERE id = ?",
            (quantity, product_id)
        )
        conn.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.close()
