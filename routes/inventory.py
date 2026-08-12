from flask import Blueprint, render_template, request, jsonify, send_file
from services import inventory_service, product_service
from utils.helpers import today_str
from utils.excel import export_with_key_mapping
import io

bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@bp.route('/')
def index():
    category = request.args.get('category', '')
    low_stock_only = request.args.get('low_stock', '') == '1'
    tab = request.args.get('tab', 'list')

    inventory = inventory_service.get_inventory_list(
        category=category or None,
        low_stock_only=low_stock_only
    )
    summary = inventory_service.get_inventory_summary()
    categories = product_service.get_categories()
    products = product_service.get_products()

    return render_template('inventory.html',
                           active_page='inventory',
                           page_title='库存管理',
                           inventory=inventory,
                           summary=summary,
                           categories=categories,
                           products=products,
                           category=category,
                           low_stock_only=low_stock_only,
                           tab=tab,
                           today=today_str())


@bp.route('/api/adjust', methods=['POST'])
def api_adjust():
    try:
        data = request.form.to_dict()
        if not data.get('product_id'):
            return jsonify({'success': False, 'message': '请选择商品'})
        change = inventory_service.adjust_stock(
            product_id=int(data['product_id']),
            new_stock=float(data['new_stock']),
            reason=data.get('reason', ''),
            notes=data.get('notes', ''),
            adjust_date=data.get('adjust_date') or None
        )
        return jsonify({'success': True, 'message': f'盘点成功，库存变动 {change:+.2f}'})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/logs')
def api_logs():
    product_id = request.args.get('product_id', '')
    logs = inventory_service.get_inventory_logs(
        product_id=int(product_id) if product_id else None
    )
    return jsonify({'success': True, 'data': logs})


@bp.route('/api/export')
def api_export():
    category = request.args.get('category', '')
    low_stock_only = request.args.get('low_stock', '') == '1'
    inventory = inventory_service.get_inventory_list(
        category=category or None, low_stock_only=low_stock_only
    )
    mapping = [
        ('商品名称', 'name'), ('分类', 'category'), ('单位', 'unit'),
        ('当前库存', 'current_stock'), ('平均成本', 'avg_cost'),
        ('库存价值', 'stock_value'), ('预警值', 'warning_stock'),
        ('默认供应商', 'supplier_name')
    ]
    content, filename = export_with_key_mapping(mapping, inventory, '库存列表.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
