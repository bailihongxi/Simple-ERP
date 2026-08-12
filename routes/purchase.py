from flask import Blueprint, render_template, request, jsonify, send_file
from services import purchase_service, product_service, supplier_service
from utils.helpers import today_str
from utils.excel import export_with_key_mapping
import io

bp = Blueprint('purchase', __name__, url_prefix='/purchase')


@bp.route('/')
def index():
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    supplier_id = request.args.get('supplier_id', '')
    keyword = request.args.get('keyword', '')
    action = request.args.get('action', '')

    purchases = purchase_service.get_purchases(
        date_start=date_start or None,
        date_end=date_end or None,
        supplier_id=supplier_id or None,
        keyword=keyword or None
    )
    stats = purchase_service.get_purchase_stats(
        date_start=date_start or None,
        date_end=date_end or None,
        supplier_id=supplier_id or None,
        keyword=keyword or None
    )
    products = product_service.get_products()
    suppliers = supplier_service.get_suppliers()

    return render_template('purchase.html',
                           active_page='purchase',
                           page_title='采购管理',
                           purchases=purchases,
                           stats=stats,
                           products=products,
                           suppliers=suppliers,
                           date_start=date_start,
                           date_end=date_end,
                           supplier_id=supplier_id,
                           keyword=keyword,
                           action=action,
                           today=today_str())


@bp.route('/api/create', methods=['POST'])
def api_create():
    try:
        data = request.form.to_dict()
        if not data.get('product_id'):
            return jsonify({'success': False, 'message': '请选择商品'})
        if not data.get('purchase_date'):
            return jsonify({'success': False, 'message': '请选择采购日期'})
        pid = purchase_service.create_purchase(data)
        return jsonify({'success': True, 'message': '采购记录添加成功', 'id': pid})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/update/<int:purchase_id>', methods=['POST'])
def api_update(purchase_id):
    try:
        data = request.form.to_dict()
        purchase_service.update_purchase(purchase_id, data)
        return jsonify({'success': True, 'message': '更新成功'})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/delete/<int:purchase_id>', methods=['POST'])
def api_delete(purchase_id):
    try:
        purchase_service.delete_purchase(purchase_id)
        return jsonify({'success': True, 'message': '删除成功'})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/get/<int:purchase_id>')
def api_get(purchase_id):
    record = purchase_service.get_purchase_by_id(purchase_id)
    if record:
        return jsonify({'success': True, 'data': record})
    return jsonify({'success': False, 'message': '记录不存在'})


@bp.route('/api/export')
def api_export():
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    supplier_id = request.args.get('supplier_id', '')
    keyword = request.args.get('keyword', '')
    purchases = purchase_service.get_purchases(
        date_start=date_start or None, date_end=date_end or None,
        supplier_id=supplier_id or None, keyword=keyword or None
    )
    mapping = [
        ('采购日期', 'purchase_date'), ('商品', 'product_name'),
        ('供应商', 'supplier_name'), ('数量', 'quantity'),
        ('单价', 'unit_price'), ('总金额', 'total_amount'),
        ('付款方式', 'payment_type'), ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, purchases, '采购记录.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
