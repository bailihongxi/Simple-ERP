import json
from database.db import query_all


def export_mobile_data():
    """
    导出手机端需要的所有数据为JSON格式
    包含：产品、采购、销售（库存数据包含在产品中）
    """
    # 产品信息（含库存、成本等）
    products = query_all("""
        SELECT id, name, brand, model, category, unit, purchase_price, sale_price,
               current_stock, avg_cost, default_supplier_id, warning_stock, notes,
               created_at, updated_at
        FROM products
        ORDER BY id DESC
    """)

    # 采购记录
    purchases = query_all("""
        SELECT p.id, p.purchase_date, p.product_id, p.supplier_id, p.quantity,
               p.unit_price, p.total_amount, p.payment_type, p.notes, p.created_at,
               pr.name as product_name, s.name as supplier_name
        FROM purchases p
        LEFT JOIN products pr ON p.product_id = pr.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.purchase_date DESC, p.id DESC
    """)

    # 销售记录
    sales = query_all("""
        SELECT s.id, s.sale_date, s.product_id, s.customer_id, s.quantity,
               s.unit_price, s.total_amount, s.cost_amount, s.profit, s.payment_type,
               s.notes, s.created_at,
               pr.name as product_name, c.name as customer_name
        FROM sales s
        LEFT JOIN products pr ON s.product_id = pr.id
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.sale_date DESC, s.id DESC
    """)

    # 供应商（备用，第一版手机端可能不用，但导出方便后续扩展）
    suppliers = query_all("""
        SELECT id, name, contact_person, phone, address, notes, created_at
        FROM suppliers
        ORDER BY id DESC
    """)

    # 客户（备用）
    customers = query_all("""
        SELECT id, name, contact_person, phone, address, notes, created_at
        FROM customers
        ORDER BY id DESC
    """)

    data = {
        'version': '1.0',
        'export_time': _get_export_time(),
        'products': products,
        'purchases': purchases,
        'sales': sales,
        'suppliers': suppliers,
        'customers': customers,
        'summary': {
            'product_count': len(products),
            'purchase_count': len(purchases),
            'sale_count': len(sales),
            'supplier_count': len(suppliers),
            'customer_count': len(customers),
        }
    }

    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def _get_export_time():
    """获取导出时间字符串"""
    from database.db import query_one
    result = query_one("SELECT datetime('now', 'localtime') as t")
    return result['t'] if result else ''
