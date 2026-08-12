from flask import Blueprint, render_template, request, jsonify, send_file
from services import purchase_service, product_service, supplier_service
from utils.helpers import today_str
from utils.excel import export_with_key_mapping, import_from_excel
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


@bp.route('/api/batch_delete', methods=['POST'])
def api_batch_delete():
    try:
        ids_str = request.form.get('ids', '')
        if not ids_str:
            return jsonify({'success': False, 'message': '请选择要删除的记录'})
        ids = [int(x) for x in ids_str.split(',') if x.strip()]
        if not ids:
            return jsonify({'success': False, 'message': '请选择要删除的记录'})
        count = purchase_service.batch_delete_purchases(ids)
        return jsonify({'success': True, 'message': f'成功删除{count}条记录'})
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


@bp.route('/api/template')
def api_template():
    """下载采购导入模板"""
    headers = ['商品名称*', '供应商名称', '采购日期*', '数量*', '单价*', '付款方式(现结/赊账)', '备注']
    rows = [['示例商品', '示例供应商', '2026-08-12', '10', '5.50', '现结', '示例备注']]
    from utils.excel import export_to_excel
    content, filename = export_to_excel(headers, rows, '采购导入模板.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@bp.route('/api/import', methods=['POST'])
def api_import():
    """从Excel导入采购记录"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择文件'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '请选择文件'})

        headers, rows = import_from_excel(file)
        if not rows:
            return jsonify({'success': False, 'message': '文件中没有数据'})

        # 获取所有商品和供应商，用于名称匹配
        all_products = product_service.get_products()
        product_map = {p['name']: p['id'] for p in all_products}
        all_suppliers = supplier_service.get_suppliers()
        supplier_map = {s['name']: s['id'] for s in all_suppliers}

        success_count = 0
        errors = []

        for idx, row in enumerate(rows, start=2):
            try:
                product_name = str(row.get('商品名称*', '') or row.get('商品名称', '') or '').strip()
                supplier_name = str(row.get('供应商名称', '') or '').strip()
                purchase_date = str(row.get('采购日期*', '') or row.get('采购日期', '') or '').strip()
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
                if not purchase_date:
                    errors.append(f'第{idx}行：采购日期不能为空')
                    continue
                if not quantity or float(quantity) <= 0:
                    errors.append(f'第{idx}行：数量必须大于0')
                    continue

                payment_type = 'credit' if payment_type_raw in ('赊账', 'credit') else 'cash'
                supplier_id = supplier_map.get(supplier_name) if supplier_name else None

                purchase_service.create_purchase({
                    'purchase_date': purchase_date,
                    'product_id': product_map[product_name],
                    'supplier_id': supplier_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'payment_type': payment_type,
                    'notes': notes
                })
                success_count += 1
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
