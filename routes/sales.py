from flask import Blueprint, render_template, request, jsonify, send_file
from services import sales_service, product_service, customer_service
from utils.helpers import today_str
from utils.excel import export_with_key_mapping
import io

bp = Blueprint('sales', __name__, url_prefix='/sales')


@bp.route('/')
def index():
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    customer_id = request.args.get('customer_id', '')
    keyword = request.args.get('keyword', '')
    action = request.args.get('action', '')

    sales = sales_service.get_sales(
        date_start=date_start or None,
        date_end=date_end or None,
        customer_id=customer_id or None,
        keyword=keyword or None
    )
    stats = sales_service.get_sales_stats(
        date_start=date_start or None,
        date_end=date_end or None,
        customer_id=customer_id or None,
        keyword=keyword or None
    )
    products = product_service.get_products()
    customers = customer_service.get_customers()

    return render_template('sales.html',
                           active_page='sales',
                           page_title='销售管理',
                           sales=sales,
                           stats=stats,
                           products=products,
                           customers=customers,
                           date_start=date_start,
                           date_end=date_end,
                           customer_id=customer_id,
                           keyword=keyword,
                           action=action,
                           today=today_str())


@bp.route('/api/create', methods=['POST'])
def api_create():
    try:
        data = request.form.to_dict()
        if not data.get('product_id'):
            return jsonify({'success': False, 'message': '请选择商品'})
        if not data.get('sale_date'):
            return jsonify({'success': False, 'message': '请选择销售日期'})
        sid = sales_service.create_sale(data)
        return jsonify({'success': True, 'message': '销售记录添加成功', 'id': sid})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/update/<int:sale_id>', methods=['POST'])
def api_update(sale_id):
    try:
        data = request.form.to_dict()
        sales_service.update_sale(sale_id, data)
        return jsonify({'success': True, 'message': '更新成功'})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/delete/<int:sale_id>', methods=['POST'])
def api_delete(sale_id):
    try:
        sales_service.delete_sale(sale_id)
        return jsonify({'success': True, 'message': '删除成功'})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/get/<int:sale_id>')
def api_get(sale_id):
    record = sales_service.get_sale_by_id(sale_id)
    if record:
        return jsonify({'success': True, 'data': record})
    return jsonify({'success': False, 'message': '记录不存在'})


@bp.route('/api/export')
def api_export():
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    customer_id = request.args.get('customer_id', '')
    keyword = request.args.get('keyword', '')
    sales = sales_service.get_sales(
        date_start=date_start or None, date_end=date_end or None,
        customer_id=customer_id or None, keyword=keyword or None
    )
    mapping = [
        ('销售日期', 'sale_date'), ('商品', 'product_name'),
        ('客户', 'customer_name'), ('数量', 'quantity'),
        ('单价', 'unit_price'), ('总金额', 'total_amount'),
        ('成本', 'cost_amount'), ('毛利', 'profit'),
        ('付款方式', 'payment_type'), ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, sales, '销售记录.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
