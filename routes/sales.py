from flask import Blueprint, render_template, request, jsonify, send_file
from services import sales_service, product_service, customer_service
from utils.helpers import today_str
from utils.excel import export_with_key_mapping, import_from_excel
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


@bp.route('/api/batch_delete', methods=['POST'])
def api_batch_delete():
    try:
        ids_str = request.form.get('ids', '')
        if not ids_str:
            return jsonify({'success': False, 'message': '请选择要删除的记录'})
        ids = [int(x) for x in ids_str.split(',') if x.strip()]
        if not ids:
            return jsonify({'success': False, 'message': '请选择要删除的记录'})
        count = sales_service.batch_delete_sales(ids)
        return jsonify({'success': True, 'message': f'成功删除{count}条记录'})
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


@bp.route('/api/template')
def api_template():
    """下载销售导入模板"""
    headers = ['商品名称*', '客户名称', '销售日期*', '数量*', '单价*', '付款方式(现结/赊账)', '备注']
    rows = [['示例商品', '示例客户', '2026-08-12', '5', '20.00', '现结', '示例备注']]
    from utils.excel import export_to_excel
    content, filename = export_to_excel(headers, rows, '销售导入模板.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@bp.route('/api/import', methods=['POST'])
def api_import():
    """从Excel导入销售记录"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择文件'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '请选择文件'})

        headers, rows = import_from_excel(file)
        if not rows:
            return jsonify({'success': False, 'message': '文件中没有数据'})

        all_products = product_service.get_products()
        product_map = {p['name']: p['id'] for p in all_products}
        all_customers = customer_service.get_customers()
        customer_map = {c['name']: c['id'] for c in all_customers}

        success_count = 0
        errors = []

        for idx, row in enumerate(rows, start=2):
            try:
                product_name = str(row.get('商品名称*', '') or row.get('商品名称', '') or '').strip()
                customer_name = str(row.get('客户名称', '') or '').strip()
                sale_date = str(row.get('销售日期*', '') or row.get('销售日期', '') or '').strip()
                quantity = str(row.get('数量*', '') or row.get('数量', '') or '').strip()
                unit_price = str(row.get('单价*', '') or row.get('单价', '') or '').strip()
                payment_type_raw = str(row.get('付款方式(现结/赊账)', '') or row.get('付款方式', '') or '').strip()
                notes = str(row.get('备注', '') or '')

                if not product_name:
                    errors.append(f'第{idx}行：商品名称不能为空')
                    continue
                if product_name not in product_map:
                    errors.append(f'第{idx}行：商品"{product_name}"不存在')
                    continue
                if not sale_date:
                    errors.append(f'第{idx}行：销售日期不能为空')
                    continue
                if not quantity or float(quantity) <= 0:
                    errors.append(f'第{idx}行：数量必须大于0')
                    continue

                payment_type = 'credit' if payment_type_raw in ('赊账', 'credit') else 'cash'
                customer_id = customer_map.get(customer_name) if customer_name else None

                sales_service.create_sale({
                    'sale_date': sale_date,
                    'product_id': product_map[product_name],
                    'customer_id': customer_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'payment_type': payment_type,
                    'notes': notes
                })
                success_count += 1
            except ValueError as e:
                errors.append(f'第{idx}行：{str(e)}')
            except Exception as e:
                errors.append(f'第{idx}行：{str(e)}')

        message = f'成功导入{success_count}条'
        if errors:
            message += f'，失败{len(errors)}条：' + '；'.join(errors[:5])
            if len(errors) > 5:
                message += f'等共{len(errors)}条错误'
        return jsonify({'success': True, 'message': message, 'added': success_count, 'errors': errors})
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'})
