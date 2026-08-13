import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import mobile_service, product_service, purchase_service, sales_service
from database.db import execute


class TestMobileHTMLExists(unittest.TestCase):
    """测试手机端HTML文件存在且包含必要元素（第二阶段功能2-6）"""

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join(BASE_DIR, 'mobile', 'index.html')
        with open(cls.html_path, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_html_file_exists(self):
        """测试手机端HTML文件存在"""
        self.assertTrue(os.path.exists(self.html_path))

    def test_html_has_doctype(self):
        """测试HTML包含DOCTYPE声明"""
        self.assertIn('<!DOCTYPE html>', self.html)

    def test_html_has_viewport(self):
        """测试HTML包含移动端viewport设置"""
        self.assertIn('viewport', self.html)
        self.assertIn('width=device-width', self.html)

    def test_html_has_bottom_nav(self):
        """测试HTML包含底部导航栏"""
        self.assertIn('tabbar', self.html)
        self.assertIn('产品', self.html)
        self.assertIn('库存', self.html)
        self.assertIn('采购', self.html)
        self.assertIn('销售', self.html)
        self.assertIn('我的', self.html)

    def test_html_has_storage_code(self):
        """测试HTML包含本地存储相关代码"""
        self.assertIn('localStorage', self.html)
        self.assertIn('initDB', self.html)
        self.assertIn('dbGetAll', self.html)
        self.assertIn('dbBulkAdd', self.html)
        self.assertIn('dbClearAll', self.html)

    def test_html_has_import_function(self):
        """测试HTML包含数据导入功能"""
        self.assertIn('handleImport', self.html)
        self.assertIn('importFile', self.html)
        self.assertIn('选择文件导入', self.html)
        self.assertIn('导入后会覆盖现有全部数据', self.html)

    def test_html_has_products_page(self):
        """测试HTML包含产品页面"""
        self.assertIn('page-products', self.html)
        self.assertIn('productKeyword', self.html)
        self.assertIn('productBrand', self.html)
        self.assertIn('productCategory', self.html)
        self.assertIn('filterProducts', self.html)
        self.assertIn('loadProducts', self.html)

    def test_html_has_inventory_page(self):
        """测试HTML包含库存页面"""
        self.assertIn('page-inventory', self.html)
        self.assertIn('invKeyword', self.html)
        self.assertIn('invBrand', self.html)
        self.assertIn('invCategory', self.html)
        self.assertIn('invLowOnly', self.html)
        self.assertIn('filterInventory', self.html)
        self.assertIn('loadInventory', self.html)
        self.assertIn('库存总价值', self.html)
        self.assertIn('低库存预警', self.html)

    def test_html_has_purchase_page(self):
        """测试HTML包含采购页面"""
        self.assertIn('page-purchase', self.html)
        self.assertIn('purDateStart', self.html)
        self.assertIn('purDateEnd', self.html)
        self.assertIn('purKeyword', self.html)
        self.assertIn('filterPurchases', self.html)
        self.assertIn('loadPurchases', self.html)
        self.assertIn('采购笔数', self.html)
        self.assertIn('采购总金额', self.html)

    def test_html_has_sales_page(self):
        """测试HTML包含销售页面"""
        self.assertIn('page-sales', self.html)
        self.assertIn('saleDateStart', self.html)
        self.assertIn('saleDateEnd', self.html)
        self.assertIn('saleKeyword', self.html)
        self.assertIn('filterSales', self.html)
        self.assertIn('loadSales', self.html)
        self.assertIn('销售笔数', self.html)
        self.assertIn('销售总金额', self.html)
        self.assertIn('总毛利', self.html)
        self.assertIn('总成本', self.html)

    def test_html_has_mine_page(self):
        """测试HTML包含我的页面"""
        self.assertIn('page-mine', self.html)
        self.assertIn('dataSummary', self.html)
        self.assertIn('数据概览', self.html)
        self.assertIn('数据导入', self.html)
        self.assertIn('关于', self.html)

    def test_html_has_switch_tab(self):
        """测试HTML包含页面切换功能"""
        self.assertIn('switchTab', self.html)
        self.assertIn('pageTitles', self.html)

    def test_html_has_toast(self):
        """测试HTML包含Toast提示"""
        self.assertIn('showToast', self.html)

    def test_html_has_money_format(self):
        """测试HTML包含金额格式化函数"""
        self.assertIn('fmtMoney', self.html)

    def test_html_no_write_operations(self):
        """测试手机端没有增删改操作（只读）"""
        self.assertNotIn('api/create', self.html)
        self.assertNotIn('api/update', self.html)
        self.assertNotIn('api/delete', self.html)
        self.assertNotIn('新增采购', self.html)
        self.assertNotIn('新增销售', self.html)
        self.assertNotIn('新增产品', self.html)
        self.assertNotIn('删除', self.html)
        self.assertNotIn('编辑', self.html)


class TestMobileDataFormat(unittest.TestCase):
    """测试手机端数据格式正确性（第二阶段）"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '手机端格式测试_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '手机端格式测试_%'")
        execute("DELETE FROM products WHERE name LIKE '手机端格式测试_%'")
        cls.product_id = product_service.create_product({
            'name': '手机端格式测试_商品', 'brand': '测试品牌',
            'category': '测试分类', 'purchase_price': '10', 'sale_price': '20',
            'warning_stock': '5'
        })
        purchase_service.create_purchase({
            'purchase_date': '2026-08-13', 'product_id': cls.product_id,
            'quantity': '10', 'unit_price': '10', 'payment_type': 'cash',
            'notes': '手机端格式测试_采购'
        })
        sales_service.create_sale({
            'sale_date': '2026-08-13', 'product_id': cls.product_id,
            'quantity': '3', 'unit_price': '20', 'payment_type': 'cash',
            'notes': '手机端格式测试_销售'
        })

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM sales WHERE notes LIKE '手机端格式测试_%'")
        execute("DELETE FROM purchases WHERE notes LIKE '手机端格式测试_%'")
        execute("DELETE FROM products WHERE name LIKE '手机端格式测试_%'")

    def test_export_json_is_valid(self):
        """测试导出的JSON格式有效"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        self.assertIsInstance(data, dict)

    def test_products_have_required_fields(self):
        """测试产品数据包含手机端需要的所有字段"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        product = next(p for p in data['products'] if p['name'] == '手机端格式测试_商品')
        required_fields = ['id', 'name', 'brand', 'category', 'current_stock',
                           'avg_cost', 'purchase_price', 'sale_price', 'warning_stock', 'unit']
        for field in required_fields:
            self.assertIn(field, product, f'产品缺少字段：{field}')

    def test_purchases_have_required_fields(self):
        """测试采购数据包含手机端需要的所有字段"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        purchase = next(p for p in data['purchases'] if p['notes'] == '手机端格式测试_采购')
        required_fields = ['id', 'purchase_date', 'product_id', 'quantity',
                           'unit_price', 'total_amount', 'payment_type', 'product_name']
        for field in required_fields:
            self.assertIn(field, purchase, f'采购缺少字段：{field}')

    def test_sales_have_required_fields(self):
        """测试销售数据包含手机端需要的所有字段"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        sale = next(s for s in data['sales'] if s['notes'] == '手机端格式测试_销售')
        required_fields = ['id', 'sale_date', 'product_id', 'quantity',
                           'unit_price', 'total_amount', 'cost_amount', 'profit',
                           'payment_type', 'product_name']
        for field in required_fields:
            self.assertIn(field, sale, f'销售缺少字段：{field}')

    def test_purchases_have_supplier_name(self):
        """测试采购数据包含供应商名称字段（即使为空）"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        purchase = next(p for p in data['purchases'] if p['notes'] == '手机端格式测试_采购')
        self.assertIn('supplier_name', purchase)

    def test_sales_have_customer_name(self):
        """测试销售数据包含客户名称字段（即使为空）"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        sale = next(s for s in data['sales'] if s['notes'] == '手机端格式测试_销售')
        self.assertIn('customer_name', sale)

    def test_summary_has_counts(self):
        """测试汇总数据包含各模块数量"""
        result = mobile_service.export_mobile_data()
        data = json.loads(result)
        self.assertIn('summary', data)
        self.assertIn('product_count', data['summary'])
        self.assertIn('purchase_count', data['summary'])
        self.assertIn('sale_count', data['summary'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
