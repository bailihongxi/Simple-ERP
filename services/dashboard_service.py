from database.db import query_all, query_one
from services import payment_service, inventory_service
from utils.helpers import today_str, month_start_str


def get_dashboard_data():
    """获取首页总览所有数据"""
    today = today_str()
    month_start = month_start_str()

    # 今日进货
    today_purchase = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total, COUNT(*) as count FROM purchases WHERE purchase_date = ?",
        (today,)
    )
    # 今日销售
    today_sale = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total, COUNT(*) as count, COALESCE(SUM(profit),0) as profit FROM sales WHERE sale_date = ?",
        (today,)
    )
    # 本月进货
    month_purchase = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total, COUNT(*) as count FROM purchases WHERE purchase_date >= ?",
        (month_start,)
    )
    # 本月销售
    month_sale = query_one(
        "SELECT COALESCE(SUM(total_amount),0) as total, COUNT(*) as count, COALESCE(SUM(profit),0) as profit FROM sales WHERE sale_date >= ?",
        (month_start,)
    )
    # 库存总价值
    inventory_value = query_one(
        "SELECT COALESCE(SUM(current_stock * avg_cost),0) as total FROM products"
    )['total']

    # 低库存预警
    low_stock = query_all(
        """SELECT p.id, p.name, p.current_stock, p.warning_stock, p.unit
           FROM products p
           WHERE p.warning_stock > 0 AND p.current_stock <= p.warning_stock
           ORDER BY (p.warning_stock - p.current_stock) DESC
           LIMIT 10"""
    )

    # 近期交易记录（采购+销售混合，最近10条）
    recent_transactions = query_all(
        """SELECT * FROM (
            SELECT 'purchase' as type, purchase_date as trans_date, pu.id as ref_id,
                   pu.total_amount, pr.name as product_name, pu.quantity, '采购' as label
            FROM purchases pu LEFT JOIN products pr ON pu.product_id = pr.id
            UNION ALL
            SELECT 'sale' as type, sale_date as trans_date, sa.id as ref_id,
                   sa.total_amount, pr.name as product_name, sa.quantity, '销售' as label
            FROM sales sa LEFT JOIN products pr ON sa.product_id = pr.id
        ) ORDER BY trans_date DESC, ref_id DESC LIMIT 10"""
    )

    return {
        'today_purchase': today_purchase,
        'today_sale': today_sale,
        'month_purchase': month_purchase,
        'month_sale': month_sale,
        'inventory_value': round(inventory_value, 2),
        'total_receivable': payment_service.get_total_receivable(),
        'total_payable': payment_service.get_total_payable(),
        'low_stock': low_stock,
        'recent_transactions': recent_transactions,
        'inventory_summary': inventory_service.get_inventory_summary()
    }
