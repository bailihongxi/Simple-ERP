import os
import sys
import webbrowser
from flask import Flask

# 确保项目根目录在路径中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from database.db import init_db
from routes import dashboard, purchase, sales, inventory, products, suppliers, customers, finance, backup


def create_app():
    app = Flask(__name__)
    app.secret_key = 'local-erp-secret-key'

    # 初始化数据库
    init_db()

    # 注册蓝图
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(purchase.bp)
    app.register_blueprint(sales.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(suppliers.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(finance.bp)
    app.register_blueprint(backup.bp)

    return app


app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  进销存管理系统启动中...")
    print("  访问地址: http://localhost:5000")
    print("  按 Ctrl+C 停止服务")
    print("=" * 50)
    # 延迟打开浏览器
    import threading
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:5000')
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
