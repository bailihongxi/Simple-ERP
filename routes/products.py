from flask import Blueprint, render_template, request, jsonify, send_file
from services import product_service, supplier_service
from utils.excel import export_with_key_mapping, import_from_excel
import io

bp = Blueprint('products', __name__, url_prefix='/products')


@bp.route('/')
def index():
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    products = product_service.get_products(keyword=keyword, category=category)
    categories = product_service.get_categories()
    suppliers = supplier_service.get_suppliers()
    return render_template('products.html',
                           active_page='products',
                           page_title='产品信息',
                           products=products,
                           categories=categories,
                           suppliers=suppliers,
                           keyword=keyword,
                           category=category)


@bp.route('/api/create', methods=['POST'])
def api_create():
    data = request.form.to_dict()
    if not data.get('name'):
        return jsonify({'success': False, 'message': '商品名称不能为空'})
    product_id = product_service.create_product(data)
    return jsonify({'success': True, 'message': '添加成功', 'id': product_id})


@bp.route('/api/update/<int:product_id>', methods=['POST'])
def api_update(product_id):
    data = request.form.to_dict()
    if not data.get('name'):
        return jsonify({'success': False, 'message': '商品名称不能为空'})
    product_service.update_product(product_id, data)
    return jsonify({'success': True, 'message': '更新成功'})


@bp.route('/api/delete/<int:product_id>', methods=['POST'])
def api_delete(product_id):
    success, msg = product_service.delete_product(product_id)
    return jsonify({'success': success, 'message': msg})


@bp.route('/api/get/<int:product_id>')
def api_get(product_id):
    product = product_service.get_product_by_id(product_id)
    if product:
        return jsonify({'success': True, 'data': product})
    return jsonify({'success': False, 'message': '产品不存在'})


@bp.route('/api/export')
def api_export():
    """导出产品列表为Excel"""
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    products = product_service.get_products(keyword=keyword or None, category=category or None)
    mapping = [
        ('商品名称', 'name'), ('分类', 'category'), ('单位', 'unit'),
        ('进货价', 'purchase_price'), ('售价', 'sale_price'),
        ('当前库存', 'current_stock'), ('平均成本', 'avg_cost'),
        ('预警值', 'warning_stock'), ('默认供应商', 'supplier_name'),
        ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, products, '产品列表.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@bp.route('/api/template')
def api_template():
    """下载产品导入模板"""
    mapping = [
        ('商品名称', 'name'), ('分类', 'category'), ('单位', 'unit'),
        ('进货价', 'purchase_price'), ('售价', 'sale_price'),
        ('预警值', 'warning_stock'), ('默认供应商', 'supplier_name'),
        ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, [], '产品导入模板.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@bp.route('/api/import', methods=['POST'])
def api_import():
    """从Excel导入产品，按名称匹配，存在则更新，不存在则新增"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择文件'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '请选择文件'})

        headers, rows = import_from_excel(file)
        if not rows:
            return jsonify({'success': False, 'message': '文件中没有数据'})

        # 构建供应商名称到ID的映射
        suppliers = supplier_service.get_suppliers()
        supplier_map = {s['name']: s['id'] for s in suppliers}

        added = 0
        updated = 0
        errors = []
        for i, row in enumerate(rows, start=2):
            name = str(row.get('商品名称', '')).strip()
            if not name:
                errors.append(f'第{i}行：商品名称为空')
                continue
            data = {
                'name': name,
                'category': str(row.get('分类', '') or ''),
                'unit': str(row.get('单位', '') or ''),
                'purchase_price': str(row.get('进货价', 0) or 0),
                'sale_price': str(row.get('售价', 0) or 0),
                'warning_stock': str(row.get('预警值', 0) or 0),
                'notes': str(row.get('备注', '') or ''),
            }
            supplier_name = str(row.get('默认供应商', '') or '').strip()
            if supplier_name and supplier_name in supplier_map:
                data['default_supplier_id'] = supplier_map[supplier_name]

            # 检查是否已存在
            existing = product_service.get_products(keyword=name)
            existing = [p for p in existing if p['name'] == name]
            if existing:
                product_service.update_product(existing[0]['id'], data)
                updated += 1
            else:
                product_service.create_product(data)
                added += 1

        return jsonify({
            'success': True,
            'message': f'导入完成：新增{added}条，更新{updated}条' + (f'，{len(errors)}条失败' if errors else ''),
            'added': added, 'updated': updated, 'errors': errors
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'})
