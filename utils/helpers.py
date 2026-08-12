from datetime import datetime, date


def format_money(value):
    """格式化金额，保留2位小数，加千分位"""
    if value is None:
        return '0.00'
    return f"{float(value):,.2f}"


def format_date(date_str):
    """格式化日期 YYYY-MM-DD -> YYYY年MM月DD日"""
    if not date_str:
        return ''
    try:
        d = datetime.strptime(date_str[:10], '%Y-%m-%d')
        return d.strftime('%Y年%m月%d日')
    except ValueError:
        return date_str


def today_str():
    """返回今天的日期字符串 YYYY-MM-DD"""
    return date.today().strftime('%Y-%m-%d')


def month_start_str():
    """返回本月第一天"""
    return date.today().replace(day=1).strftime('%Y-%m-%d')


def now_str():
    """返回当前时间字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
