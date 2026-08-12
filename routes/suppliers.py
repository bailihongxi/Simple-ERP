from flask import Blueprint, render_template, request, jsonify, send_file
from services import supplier_service, payment_service
from utils.excel import export_with_key_mapping, import_from_excel
import io

bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')


@bp.route('/')
def index():
    keyword = request.args.get('keyword', '')
    suppliers = supplier_service.get_suppliers(keyword=keyword)
    return render_template('suppliers.html',
                           active_page='suppliers',
                           page_title='供应商信息',
                           suppliers=suppliers,
                           keyword=keyword)


@bp.route('/api/create', methods=['POST'])
def api_create():
    data = request.form.to_dict()
    if not data.get('name'):
        return jsonify({'success': False, 'message': '供应商名称不能为空'})
    sid = supplier_service.create_supplier(data)
    return jsonify({'success': True, 'message': '添加成功', 'id': sid})


@bp.route('/api/update/<int:supplier_id>', methods=['POST'])
def api_update(supplier_id):
    data = request.form.to_dict()
    if not data.get('name'):
        return jsonify({'success': False, 'message': '供应商名称不能为空'})
    supplier_service.update_supplier(supplier_id, data)
    return jsonify({'success': True, 'message': '更新成功'})


@bp.route('/api/delete/<int:supplier_id>', methods=['POST'])
def api_delete(supplier_id):
    success, msg = supplier_service.delete_supplier(supplier_id)
    return jsonify({'success': success, 'message': msg})


@bp.route('/api/get/<int:supplier_id>')
def api_get(supplier_id):
    supplier = supplier_service.get_supplier_by_id(supplier_id)
    if supplier:
        return jsonify({'success': True, 'data': supplier})
    return jsonify({'success': False, 'message': '供应商不存在'})


@bp.route('/api/detail/<int:supplier_id>')
def api_detail(supplier_id):
    supplier = supplier_service.get_supplier_by_id(supplier_id)
    if not supplier:
        return jsonify({'success': False, 'message': '供应商不存在'})
    purchases = supplier_service.get_supplier_purchases(supplier_id)
    payable = supplier_service.get_supplier_payable(supplier_id)
    payments = payment_service.get_payments(party_type='supplier', party_id=supplier_id)
    return jsonify({
        'success': True,
        'data': supplier,
        'purchases': purchases,
        'payable': payable,
        'payments': payments
    })


@bp.route('/api/pay/<int:supplier_id>', methods=['POST'])
def api_pay(supplier_id):
    try:
        data = request.form.to_dict()
        data['type'] = 'pay'
        data['party_type'] = 'supplier'
        data['party_id'] = supplier_id
        pid = payment_service.create_payment(data)
        return jsonify({'success': True, 'message': '付款记录添加成功', 'id': pid})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/export')
def api_export():
    suppliers = supplier_service.get_suppliers()
    mapping = [
        ('供应商名称', 'name'), ('联系人', 'contact_person'),
        ('电话', 'phone'), ('地址', 'address'), ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, suppliers, '供应商列表.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@bp.route('/api/template')
def api_template():
    mapping = [
        ('供应商名称', 'name'), ('联系人', 'contact_person'),
        ('电话', 'phone'), ('地址', 'address'), ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, [], '供应商导入模板.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@bp.route('/api/import', methods=['POST'])
def api_import():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请选择文件'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '请选择文件'})
        headers, rows = import_from_excel(file)
        if not rows:
            return jsonify({'success': False, 'message': '文件中没有数据'})
        added = 0
        updated = 0
        errors = []
        for i, row in enumerate(rows, start=2):
            name = str(row.get('供应商名称', '')).strip()
            if not name:
                errors.append(f'第{i}行：名称为空')
                continue
            data = {
                'name': name,
                'contact_person': str(row.get('联系人', '') or ''),
                'phone': str(row.get('电话', '') or ''),
                'address': str(row.get('地址', '') or ''),
                'notes': str(row.get('备注', '') or ''),
            }
            existing = supplier_service.get_suppliers(keyword=name)
            existing = [s for s in existing if s['name'] == name]
            if existing:
                supplier_service.update_supplier(existing[0]['id'], data)
                updated += 1
            else:
                supplier_service.create_supplier(data)
                added += 1
        return jsonify({
            'success': True,
            'message': f'导入完成：新增{added}条，更新{updated}条' + (f'，{len(errors)}条失败' if errors else ''),
            'added': added, 'updated': updated, 'errors': errors
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'})
