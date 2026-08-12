from database.db import query_all, query_one, execute


def get_products(keyword=None, category=None):
    """获取产品列表，支持按名称搜索和分类筛选"""
    sql = """
        SELECT p.*, s.name as supplier_name
        FROM products p
        LEFT JOIN suppliers s ON p.default_supplier_id = s.id
        WHERE 1=1
    """
    params = []
    if keyword:
        sql += " AND p.name LIKE ?"
        params.append(f"%{keyword}%")
    if category:
        sql += " AND p.category = ?"
        params.append(category)
    sql += " ORDER BY p.id DESC"
    return query_all(sql, params)


def get_product_by_id(product_id):
    """根据ID获取产品"""
    sql = """
        SELECT p.*, s.name as supplier_name
        FROM products p
        LEFT JOIN suppliers s ON p.default_supplier_id = s.id
        WHERE p.id = ?
    """
    return query_one(sql, (product_id,))


def get_categories():
    """获取所有分类（去重）"""
    sql = "SELECT DISTINCT category FROM products WHERE category != '' ORDER BY category"
    rows = query_all(sql)
    return [r['category'] for r in rows if r['category']]


def create_product(data):
    """创建产品"""
    sql = """
        INSERT INTO products (name, brand, model, category, unit, purchase_price, sale_price,
                              default_supplier_id, warning_stock, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return execute(sql, (
        data.get('name', ''),
        data.get('brand', ''),
        data.get('model', ''),
        data.get('category', ''),
        data.get('unit', ''),
        float(data.get('purchase_price', 0) or 0),
        float(data.get('sale_price', 0) or 0),
        data.get('default_supplier_id') or None,
        float(data.get('warning_stock', 0) or 0),
        data.get('notes', '')
    ))


def update_product(product_id, data):
    """更新产品"""
    sql = """
        UPDATE products SET
            name = ?, brand = ?, model = ?, category = ?, unit = ?,
            purchase_price = ?, sale_price = ?,
            default_supplier_id = ?, warning_stock = ?, notes = ?,
            updated_at = datetime('now', 'localtime')
        WHERE id = ?
    """
    execute(sql, (
        data.get('name', ''),
        data.get('brand', ''),
        data.get('model', ''),
        data.get('category', ''),
        data.get('unit', ''),
        float(data.get('purchase_price', 0) or 0),
        float(data.get('sale_price', 0) or 0),
        data.get('default_supplier_id') or None,
        float(data.get('warning_stock', 0) or 0),
        data.get('notes', ''),
        product_id
    ))


def delete_product(product_id):
    """删除产品（有关联记录时不可删除）"""
    ref = check_product_references(product_id)
    if ref['has_reference']:
        return False, ref['message']
    execute("DELETE FROM products WHERE id = ?", (product_id,))
    return True, '删除成功'


def check_product_references(product_id):
    """检查产品是否有关联的采购或销售记录"""
    purchase_count = query_one("SELECT COUNT(*) as cnt FROM purchases WHERE product_id = ?", (product_id,))['cnt']
    sale_count = query_one("SELECT COUNT(*) as cnt FROM sales WHERE product_id = ?", (product_id,))['cnt']
    adj_count = query_one("SELECT COUNT(*) as cnt FROM inventory_adjustments WHERE product_id = ?", (product_id,))['cnt']
    total = purchase_count + sale_count + adj_count
    if total > 0:
        return {
            'has_reference': True,
            'message': f'该产品有关联记录（采购{purchase_count}条、销售{sale_count}条、盘点{adj_count}条），无法删除'
        }
    return {'has_reference': False, 'message': ''}
