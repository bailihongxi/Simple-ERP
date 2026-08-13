from flask import Blueprint, render_template, request, jsonify, send_file
from services import backup_service, mobile_service
import io

bp = Blueprint('backup', __name__, url_prefix='/backup')


@bp.route('/')
def index():
    backups = backup_service.list_backups()
    return render_template('backup.html',
                           active_page='backup',
                           page_title='数据备份与恢复',
                           backups=backups)


@bp.route('/api/create', methods=['POST'])
def api_create():
    try:
        path = backup_service.create_backup()
        return jsonify({'success': True, 'message': '备份创建成功', 'path': path})
    except Exception as e:
        return jsonify({'success': False, 'message': f'备份失败：{str(e)}'})


@bp.route('/api/restore', methods=['POST'])
def api_restore():
    try:
        filename = request.form.get('filename', '')
        if not filename:
            return jsonify({'success': False, 'message': '请选择备份文件'})
        before_path = backup_service.restore_backup(filename)
        return jsonify({
            'success': True,
            'message': '恢复成功，当前数据已自动备份，页面即将刷新',
            'before_restore_path': before_path
        })
    except FileNotFoundError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'恢复失败：{str(e)}'})


@bp.route('/api/delete', methods=['POST'])
def api_delete():
    try:
        filename = request.form.get('filename', '')
        if not filename:
            return jsonify({'success': False, 'message': '请选择备份文件'})
        backup_service.delete_backup(filename)
        return jsonify({'success': True, 'message': '备份已删除'})
    except FileNotFoundError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})


@bp.route('/api/export_mobile')
def api_export_mobile():
    """导出手机端数据（JSON格式）"""
    try:
        json_data = mobile_service.export_mobile_data()
        buf = io.BytesIO(json_data.encode('utf-8'))
        buf.seek(0)
        from utils.helpers import today_str
        filename = f'手机端数据_{today_str()}.json'
        return send_file(buf, as_attachment=True, download_name=filename,
                         mimetype='application/json')
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败：{str(e)}'})
