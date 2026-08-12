from database.db import query_all, query_one
from services import payment_service
from utils.helpers import month_start_str


def get_finance_summary(date_start=None, date_end=None):
    """
    财务汇总（指定时间段）
    - 总收入 = 现结销售合计 + 客户收款合计
    - 总支出 = 现结采购合计 + 供应商付款合计
    - 毛利 = 所有销售profit合计
    - 销售总额 = 所有销售total_amount合计
    """
    # 现结销售
    cash_sales_sql = "SELECT COALESCE(SUM(total_amount),0) as total FROM sales WHERE payment_type = 'cash'"
    cash_sales_params = []
    if date_start:
        cash_sales_sql += " AND sale_date >= ?"
        cash_sales_params.append(date_start)
    if date_end:
        cash_sales_sql += " AND sale_date <= ?"
        cash_sales_params.append(date_end)
    cash_sales = query_one(cash_sales_sql, cash_sales_params)['total']

    # 客户收款
    received_sql = "SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE party_type = 'customer' AND type = 'receive'"
    received_params = []
    if date_start:
        received_sql += " AND payment_date >= ?"
        received_params.append(date_start)
    if date_end:
        received_sql += " AND payment_date <= ?"
        received_params.append(date_end)
    received = query_one(received_sql, received_params)['total']

    # 现结采购
    cash_purchase_sql = "SELECT COALESCE(SUM(total_amount),0) as total FROM purchases WHERE payment_type = 'cash'"
    cash_purchase_params = []
    if date_start:
        cash_purchase_sql += " AND purchase_date >= ?"
        cash_purchase_params.append(date_start)
    if date_end:
        cash_purchase_sql += " AND purchase_date <= ?"
        cash_purchase_params.append(date_end)
    cash_purchases = query_one(cash_purchase_sql, cash_purchase_params)['total']

    # 供应商付款
    paid_sql = "SELECT COALESCE(SUM(amount),0) as total FROM payments WHERE party_type = 'supplier' AND type = 'pay'"
    paid_params = []
    if date_start:
        paid_sql += " AND payment_date >= ?"
        paid_params.append(date_start)
    if date_end:
        paid_sql += " AND payment_date <= ?"
        paid_params.append(date_end)
    paid = query_one(paid_sql, paid_params)['total']

    # 销售总额和毛利（所有销售，含赊账）
    sales_sql = "SELECT COALESCE(SUM(total_amount),0) as total_amount, COALESCE(SUM(profit),0) as total_profit, COUNT(*) as count FROM sales WHERE 1=1"
    sales_params = []
    if date_start:
        sales_sql += " AND sale_date >= ?"
        sales_params.append(date_start)
    if date_end:
        sales_sql += " AND sale_date <= ?"
        sales_params.append(date_end)
    sales_stats = query_one(sales_sql, sales_params)

    total_income = round(cash_sales + received, 2)
    total_expense = round(cash_purchases + paid, 2)
    net_profit = round(total_income - total_expense, 2)
    gross_profit = round(sales_stats['total_profit'], 2)
    gross_margin = round(gross_profit / sales_stats['total_amount'] * 100, 2) if sales_stats['total_amount'] > 0 else 0

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'gross_profit': gross_profit,
        'gross_margin': gross_margin,
        'sales_total': round(sales_stats['total_amount'], 2),
        'sales_count': sales_stats['count'],
        'cash_sales': round(cash_sales, 2),
        'received': round(received, 2),
        'cash_purchases': round(cash_purchases, 2),
        'paid': round(paid, 2),
        'total_receivable': payment_service.get_total_receivable(),
        'total_payable': payment_service.get_total_payable()
    }


def get_payment_records(date_start=None, date_end=None, ptype=None):
    """
    收付款记录列表（联合显示）
    ptype: 'receive' / 'pay' / None(全部)
    """
    sql = """
        SELECT p.*,
               CASE WHEN p.party_type = 'supplier' THEN s.name ELSE c.name END as party_name
        FROM payments p
        LEFT JOIN suppliers s ON p.party_type = 'supplier' AND p.party_id = s.id
        LEFT JOIN customers c ON p.party_type = 'customer' AND p.party_id = c.id
        WHERE 1=1
    """
    params = []
    if date_start:
        sql += " AND p.payment_date >= ?"
        params.append(date_start)
    if date_end:
        sql += " AND p.payment_date <= ?"
        params.append(date_end)
    if ptype:
        sql += " AND p.type = ?"
        params.append(ptype)
    sql += " ORDER BY p.payment_date DESC, p.id DESC"
    return query_all(sql, params)


def get_monthly_trend(months=6):
    """
    最近N个月的收入/支出/毛利趋势
    返回列表，每项含 month, income, expense, gross_profit
    """
    import datetime
    today = datetime.date.today()
    results = []
    for i in range(months - 1, -1, -1):
        # 计算第i个月的起止
        first = today.replace(day=1)
        if i > 0:
            # 往前推i个月
            month = first.month - i
            year = first.year
            while month <= 0:
                month += 12
                year -= 1
            start = datetime.date(year, month, 1)
        else:
            start = first
        # 下个月第一天
        if start.month == 12:
            next_start = datetime.date(start.year + 1, 1, 1)
        else:
            next_start = datetime.date(start.year, start.month + 1, 1)
        end = next_start - datetime.timedelta(days=1)

        summary = get_finance_summary(
            date_start=start.strftime('%Y-%m-%d'),
            date_end=end.strftime('%Y-%m-%d')
        )
        results.append({
            'month': start.strftime('%Y-%m'),
            'income': summary['total_income'],
            'expense': summary['total_expense'],
            'gross_profit': summary['gross_profit']
        })
    return results
