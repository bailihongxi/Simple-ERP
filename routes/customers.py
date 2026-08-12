from flask import Blueprint, render_template, request, jsonify, send_file
from services import customer_service, payment_service
from utils.excel import export_with_key_mapping, import_from_excel
import io

bp = Blueprint('customers', __name__, url_prefix='/customers')


@bp.route('/')
def index():
    keyword = request.args.get('keyword', '')
    customers = customer_service.get_customers(keyword=keyword)
    return render_template('customers.html',
                           active_page='customers',
                           page_title='客户信息',
                           customers=customers,
                           keyword=keyword)


@bp.route('/api/create', methods=['POST'])
def api_create():
    data = request.form.to_dict()
    if not data.get('name'):
        return jsonify({'success': False, 'message': '客户名称不能为空'})
    cid = customer_service.create_customer(data)
    return jsonify({'success': True, 'message': '添加成功', 'id': cid})


@bp.route('/api/update/<int:customer_id>', methods=['POST'])
def api_update(customer_id):
    data = request.form.to_dict()
    if not data.get('name'):
        return jsonify({'success': False, 'message': '客户名称不能为空'})
    customer_service.update_customer(customer_id, data)
    return jsonify({'success': True, 'message': '更新成功'})


@bp.route('/api/delete/<int:customer_id>', methods=['POST'])
def api_delete(customer_id):
    success, msg = customer_service.delete_customer(customer_id)
    return jsonify({'success': success, 'message': msg})


@bp.route('/api/get/<int:customer_id>')
def api_get(customer_id):
    customer = customer_service.get_customer_by_id(customer_id)
    if customer:
        return jsonify({'success': True, 'data': customer})
    return jsonify({'success': False, 'message': '客户不存在'})


@bp.route('/api/detail/<int:customer_id>')
def api_detail(customer_id):
    customer = customer_service.get_customer_by_id(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': '客户不存在'})
    sales = customer_service.get_customer_sales(customer_id)
    receivable = customer_service.get_customer_receivable(customer_id)
    payments = payment_service.get_payments(party_type='customer', party_id=customer_id)
    return jsonify({
        'success': True,
        'data': customer,
        'sales': sales,
        'receivable': receivable,
        'payments': payments
    })


@bp.route('/api/receive/<int:customer_id>', methods=['POST'])
def api_receive(customer_id):
    try:
        data = request.form.to_dict()
        data['type'] = 'receive'
        data['party_type'] = 'customer'
        data['party_id'] = customer_id
        pid = payment_service.create_payment(data)
        return jsonify({'success': True, 'message': '收款记录添加成功', 'id': pid})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})


@bp.route('/api/export')
def api_export():
    customers = customer_service.get_customers()
    mapping = [
        ('客户名称', 'name'), ('联系人', 'contact_person'),
        ('电话', 'phone'), ('地址', 'address'), ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, customers, '客户列表.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@bp.route('/api/template')
def api_template():
    mapping = [
        ('客户名称', 'name'), ('联系人', 'contact_person'),
        ('电话', 'phone'), ('地址', 'address'), ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, [], '客户导入模板.xlsx')
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
            name = str(row.get('客户名称', '')).strip()
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
            existing = customer_service.get_customers(keyword=name)
            existing = [c for c in existing if c['name'] == name]
            if existing:
                customer_service.update_customer(existing[0]['id'], data)
                updated += 1
            else:
                customer_service.create_customer(data)
                added += 1
        return jsonify({
            'success': True,
            'message': f'导入完成：新增{added}条，更新{updated}条' + (f'，{len(errors)}条失败' if errors else ''),
            'added': added, 'updated': updated, 'errors': errors
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'})
