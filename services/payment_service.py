from database.db import query_all, query_one, execute
from utils.helpers import today_str


def create_payment(data):
    """
    创建收付款记录
    type: 'pay'（付款给供应商）或 'receive'（收款）
    party_type: 'supplier' 或 'customer'
    """
    payment_date = data.get('payment_date') or today_str()
    ptype = data.get('type')  # pay / receive
    party_type = data.get('party_type')  # supplier / customer
    party_id = int(data['party_id'])
    amount = float(data['amount'])
    notes = data.get('notes', '')

    if amount <= 0:
        raise ValueError('金额必须大于0')
    if ptype not in ('pay', 'receive'):
        raise ValueError('收付款类型错误')
    if party_type not in ('supplier', 'customer'):
        raise ValueError('往来对象类型错误')

    # 校验：付款给供应商时 type 应为 pay；客户收款时 type 应为 receive
    if party_type == 'supplier' and ptype != 'pay':
        raise ValueError('供应商应为付款记录')
    if party_type == 'customer' and ptype != 'receive':
        raise ValueError('客户应为收款记录')

    return execute(
        """INSERT INTO payments (payment_date, type, party_type, party_id, amount, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (payment_date, ptype, party_type, party_id, amount, notes)
    )


def get_payments(party_type=None, party_id=None, ptype=None):
    """查询收付款记录"""
    sql = "SELECT * FROM payments WHERE 1=1"
    params = []
    if party_type:
        sql += " AND party_type = ?"
        params.append(party_type)
    if party_id:
        sql += " AND party_id = ?"
        params.append(party_id)
    if ptype:
        sql += " AND type = ?"
        params.append(ptype)
    sql += " ORDER BY payment_date DESC, id DESC"
    return query_all(sql, params)


def get_payment_by_id(payment_id):
    return query_one("SELECT * FROM payments WHERE id = ?", (payment_id,))


def delete_payment(payment_id):
    execute("DELETE FROM payments WHERE id = ?", (payment_id,))


def get_total_receivable():
    """计算总应收 = 所有客户赊账销售 - 所有客户收款"""
    credit_sales = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total FROM sales WHERE payment_type = 'credit'"
    )['total']
    received = query_one(
        "SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE party_type = 'customer' AND type = 'receive'"
    )['total']
    return round(credit_sales - received, 2)


def get_total_payable():
    """计算总应付 = 所有供应商赊账采购 - 所有供应商付款"""
    credit_purchases = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total FROM purchases WHERE payment_type = 'credit'"
    )['total']
    paid = query_one(
        "SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE party_type = 'supplier' AND type = 'pay'"
    )['total']
    return round(credit_purchases - paid, 2)
