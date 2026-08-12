from database.db import query_all, query_one, execute


def get_customers(keyword=None):
    """获取客户列表，含应收余额"""
    sql = """
        SELECT c.*,
            COALESCE((
                SELECT SUM(s.total_amount) FROM sales s
                WHERE s.customer_id = c.id AND s.payment_type = 'credit'
            ), 0) AS credit_total,
            COALESCE((
                SELECT SUM(pay.amount) FROM payments pay
                WHERE pay.party_type = 'customer' AND pay.party_id = c.id AND pay.type = 'receive'
            ), 0) AS received_total
        FROM customers c
        WHERE 1=1
    """
    params = []
    if keyword:
        sql += " AND c.name LIKE ?"
        params.append(f"%{keyword}%")
    sql += " ORDER BY c.id DESC"
    rows = query_all(sql, params)
    for r in rows:
        r['receivable_balance'] = round(r['credit_total'] - r['received_total'], 2)
    return rows


def get_customer_by_id(customer_id):
    """根据ID获取客户"""
    sql = "SELECT * FROM customers WHERE id = ?"
    return query_one(sql, (customer_id,))


def get_customer_receivable(customer_id):
    """计算客户应收余额"""
    credit = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total FROM sales WHERE customer_id = ? AND payment_type = 'credit'",
        (customer_id,)
    )['total']
    received = query_one(
        "SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE party_type = 'customer' AND party_id = ? AND type = 'receive'",
        (customer_id,)
    )['total']
    return round(credit - received, 2)


def get_customer_sales(customer_id):
    """获取客户历史销售记录"""
    sql = """
        SELECT s.*, p.name as product_name
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        WHERE s.customer_id = ?
        ORDER BY s.sale_date DESC, s.id DESC
    """
    return query_all(sql, (customer_id,))


def create_customer(data):
    """创建客户"""
    sql = """
        INSERT INTO customers (name, contact_person, phone, address, notes)
        VALUES (?, ?, ?, ?, ?)
    """
    return execute(sql, (
        data.get('name', ''),
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('address', ''),
        data.get('notes', '')
    ))


def update_customer(customer_id, data):
    """更新客户"""
    sql = """
        UPDATE customers SET name = ?, contact_person = ?, phone = ?, address = ?, notes = ?
        WHERE id = ?
    """
    execute(sql, (
        data.get('name', ''),
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('address', ''),
        data.get('notes', ''),
        customer_id
    ))


def delete_customer(customer_id):
    """删除客户（有关联销售时不可删除）"""
    ref = check_customer_references(customer_id)
    if ref['has_reference']:
        return False, ref['message']
    execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    return True, '删除成功'


def check_customer_references(customer_id):
    """检查客户是否有关联记录"""
    sale_count = query_one("SELECT COUNT(*) as cnt FROM sales WHERE customer_id = ?", (customer_id,))['cnt']
    payment_count = query_one("SELECT COUNT(*) as cnt FROM payments WHERE party_type = 'customer' AND party_id = ?", (customer_id,))['cnt']
    total = sale_count + payment_count
    if total > 0:
        return {
            'has_reference': True,
            'message': f'该客户有关联记录（销售{sale_count}条、收款{payment_count}条），无法删除'
        }
    return {'has_reference': False, 'message': ''}
