from flask import Blueprint, render_template, request, jsonify, send_file
from services import finance_service
from utils.helpers import today_str, month_start_str
from utils.excel import export_with_key_mapping
import io

bp = Blueprint('finance', __name__, url_prefix='/finance')


@bp.route('/')
def index():
    date_start = request.args.get('date_start', month_start_str())
    date_end = request.args.get('date_end', today_str())
    ptype = request.args.get('ptype', '')

    summary = finance_service.get_finance_summary(
        date_start=date_start or None,
        date_end=date_end or None
    )
    records = finance_service.get_payment_records(
        date_start=date_start or None,
        date_end=date_end or None,
        ptype=ptype or None
    )
    trend = finance_service.get_monthly_trend(6)

    return render_template('finance.html',
                           active_page='finance',
                           page_title='财务信息',
                           summary=summary,
                           records=records,
                           trend=trend,
                           date_start=date_start,
                           date_end=date_end,
                           ptype=ptype)


@bp.route('/api/summary')
def api_summary():
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    summary = finance_service.get_finance_summary(
        date_start=date_start or None,
        date_end=date_end or None
    )
    return jsonify({'success': True, 'data': summary})


@bp.route('/api/export')
def api_export():
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    ptype = request.args.get('ptype', '')
    records = finance_service.get_payment_records(
        date_start=date_start or None, date_end=date_end or None,
        ptype=ptype or None
    )
    mapping = [
        ('日期', 'payment_date'), ('类型', 'type'),
        ('往来对象', 'party_name'), ('金额', 'amount'), ('备注', 'notes')
    ]
    content, filename = export_with_key_mapping(mapping, records, '财务记录.xlsx')
    return send_file(io.BytesIO(content), as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
