from flask import Blueprint, render_template, jsonify
from services import dashboard_service

bp = Blueprint('dashboard', __name__, url_prefix='/')


@bp.route('/')
def index():
    data = dashboard_service.get_dashboard_data()
    return render_template('dashboard.html',
                           active_page='dashboard',
                           page_title='首页总览',
                           **data)


@bp.route('/api/dashboard')
def api_dashboard():
    data = dashboard_service.get_dashboard_data()
    return jsonify({'success': True, 'data': data})
