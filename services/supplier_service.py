from database.db import query_all, query_one, execute


def get_suppliers(keyword=None):
    """获取供应商列表，含应付余额"""
    sql = """
        SELECT s.*,
            COALESCE((
                SELECT SUM(p.total_amount) FROM purchases p
                WHERE p.supplier_id = s.id AND p.payment_type = 'credit'
            ), 0) AS credit_total,
            COALESCE((
                SELECT SUM(pay.amount) FROM payments pay
                WHERE pay.party_type = 'supplier' AND pay.party_id = s.id AND pay.type = 'pay'
            ), 0) AS paid_total
        FROM suppliers s
        WHERE 1=1
    """
    params = []
    if keyword:
        sql += " AND s.name LIKE ?"
        params.append(f"%{keyword}%")
    sql += " ORDER BY s.id DESC"
    rows = query_all(sql, params)
    for r in rows:
        r['payable_balance'] = round(r['credit_total'] - r['paid_total'], 2)
    return rows


def get_supplier_by_id(supplier_id):
    """根据ID获取供应商"""
    sql = "SELECT * FROM suppliers WHERE id = ?"
    return query_one(sql, (supplier_id,))


def get_supplier_payable(supplier_id):
    """计算供应商应付余额"""
    credit = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total FROM purchases WHERE supplier_id = ? AND payment_type = 'credit'",
        (supplier_id,)
    )['total']
    paid = query_one(
        "SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE party_type = 'supplier' AND party_id = ? AND type = 'pay'",
        (supplier_id,)
    )['total']
    return round(credit - paid, 2)


def get_supplier_purchases(supplier_id):
    """获取供应商历史采购记录"""
    sql = """
        SELECT p.*, pr.name as product_name
        FROM purchases p
        LEFT JOIN products pr ON p.product_id = pr.id
        WHERE p.supplier_id = ?
        ORDER BY p.purchase_date DESC, p.id DESC
    """
    return query_all(sql, (supplier_id,))


def create_supplier(data):
    """创建供应商"""
    sql = """
        INSERT INTO suppliers (name, contact_person, phone, address, notes)
        VALUES (?, ?, ?, ?, ?)
    """
    return execute(sql, (
        data.get('name', ''),
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('address', ''),
        data.get('notes', '')
    ))


def update_supplier(supplier_id, data):
    """更新供应商"""
    sql = """
        UPDATE suppliers SET name = ?, contact_person = ?, phone = ?, address = ?, notes = ?
        WHERE id = ?
    """
    execute(sql, (
        data.get('name', ''),
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('address', ''),
        data.get('notes', ''),
        supplier_id
    ))


def delete_supplier(supplier_id):
    """删除供应商（有关联采购时不可删除）"""
    ref = check_supplier_references(supplier_id)
    if ref['has_reference']:
        return False, ref['message']
    execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
    return True, '删除成功'


def check_supplier_references(supplier_id):
    """检查供应商是否有关联记录"""
    purchase_count = query_one("SELECT COUNT(*) as cnt FROM purchases WHERE supplier_id = ?", (supplier_id,))['cnt']
    payment_count = query_one("SELECT COUNT(*) as cnt FROM payments WHERE party_type = 'supplier' AND party_id = ?", (supplier_id,))['cnt']
    product_count = query_one("SELECT COUNT(*) as cnt FROM products WHERE default_supplier_id = ?", (supplier_id,))['cnt']
    total = purchase_count + payment_count + product_count
    if total > 0:
        return {
            'has_reference': True,
            'message': f'该供应商有关联记录（采购{purchase_count}条、付款{payment_count}条、默认产品{product_count}个），无法删除'
        }
    return {'has_reference': False, 'message': ''}
