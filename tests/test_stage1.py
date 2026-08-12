import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services import product_service, supplier_service, customer_service
from database.db import execute


class TestProductService(unittest.TestCase):
    """测试产品服务层"""

    @classmethod
    def setUpClass(cls):
        # 清理可能残留的测试数据
        execute("DELETE FROM products WHERE name LIKE '测试产品_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '测试产品_%'")

    def test_create_product(self):
        """测试创建产品"""
        data = {
            'name': '测试产品_001',
            'category': '测试分类',
            'unit': '个',
            'purchase_price': '10.5',
            'sale_price': '15.0',
            'warning_stock': '5',
            'notes': '测试备注'
        }
        pid = product_service.create_product(data)
        self.assertIsNotNone(pid)
        self.assertGreater(pid, 0)
        # 验证创建
        p = product_service.get_product_by_id(pid)
        self.assertEqual(p['name'], '测试产品_001')
        self.assertEqual(p['category'], '测试分类')
        self.assertEqual(float(p['purchase_price']), 10.5)
        self.assertEqual(float(p['current_stock']), 0)
        self.assertEqual(float(p['avg_cost']), 0)

    def test_update_product(self):
        """测试更新产品"""
        pid = product_service.create_product({'name': '测试产品_002', 'category': '旧分类'})
        product_service.update_product(pid, {'name': '测试产品_002_改', 'category': '新分类', 'purchase_price': '20'})
        p = product_service.get_product_by_id(pid)
        self.assertEqual(p['name'], '测试产品_002_改')
        self.assertEqual(p['category'], '新分类')
        self.assertEqual(float(p['purchase_price']), 20)

    def test_delete_product_no_ref(self):
        """测试删除无关联的产品"""
        pid = product_service.create_product({'name': '测试产品_003'})
        success, msg = product_service.delete_product(pid)
        self.assertTrue(success)
        self.assertIsNone(product_service.get_product_by_id(pid))

    def test_delete_product_with_ref(self):
        """测试有关联记录的产品不可删除"""
        pid = product_service.create_product({'name': '测试产品_004'})
        # 插入一条采购记录制造关联
        execute("INSERT INTO purchases (purchase_date, product_id, quantity, unit_price, total_amount, payment_type) VALUES ('2026-01-01', ?, 10, 5, 50, 'cash')", (pid,))
        success, msg = product_service.delete_product(pid)
        self.assertFalse(success)
        self.assertIn('无法删除', msg)
        # 清理关联
        execute("DELETE FROM purchases WHERE product_id = ?", (pid,))
        product_service.delete_product(pid)

    def test_get_products_keyword(self):
        """测试按名称搜索"""
        product_service.create_product({'name': '测试产品_搜索A'})
        product_service.create_product({'name': '测试产品_搜索B'})
        results = product_service.get_products(keyword='搜索A')
        names = [r['name'] for r in results]
        self.assertIn('测试产品_搜索A', names)
        self.assertNotIn('测试产品_搜索B', names)

    def test_get_categories(self):
        """测试获取分类列表"""
        product_service.create_product({'name': '测试产品_cat1', 'category': '分类X'})
        product_service.create_product({'name': '测试产品_cat2', 'category': '分类Y'})
        cats = product_service.get_categories()
        self.assertIn('分类X', cats)
        self.assertIn('分类Y', cats)

    def test_empty_name_validation(self):
        """测试空名称在路由层被拦截（通过API测试）"""
        from app import create_app
        app = create_app()
        client = app.test_client()
        resp = client.post('/products/api/create', data={'name': ''})
        data = resp.get_json()
        self.assertFalse(data['success'])
        self.assertIn('不能为空', data['message'])


class TestSupplierService(unittest.TestCase):
    """测试供应商服务层"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM suppliers WHERE name LIKE '测试供应商_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM suppliers WHERE name LIKE '测试供应商_%'")

    def test_create_and_get(self):
        sid = supplier_service.create_supplier({
            'name': '测试供应商_001',
            'contact_person': '张三',
            'phone': '13800138000',
            'address': '测试地址',
            'notes': '测试'
        })
        self.assertGreater(sid, 0)
        s = supplier_service.get_supplier_by_id(sid)
        self.assertEqual(s['name'], '测试供应商_001')
        self.assertEqual(s['contact_person'], '张三')

    def test_update(self):
        sid = supplier_service.create_supplier({'name': '测试供应商_002'})
        supplier_service.update_supplier(sid, {'name': '测试供应商_002_改', 'phone': '13900139000'})
        s = supplier_service.get_supplier_by_id(sid)
        self.assertEqual(s['name'], '测试供应商_002_改')
        self.assertEqual(s['phone'], '13900139000')

    def test_delete_no_ref(self):
        sid = supplier_service.create_supplier({'name': '测试供应商_003'})
        success, msg = supplier_service.delete_supplier(sid)
        self.assertTrue(success)
        self.assertIsNone(supplier_service.get_supplier_by_id(sid))

    def test_delete_with_ref(self):
        sid = supplier_service.create_supplier({'name': '测试供应商_004'})
        pid = product_service.create_product({'name': '测试产品_supplier_ref', 'default_supplier_id': str(sid)})
        success, msg = supplier_service.delete_supplier(sid)
        self.assertFalse(success)
        self.assertIn('无法删除', msg)
        # 清理
        product_service.delete_product(pid)
        supplier_service.delete_supplier(sid)

    def test_payable_balance_zero(self):
        """测试无交易时应付余额为0"""
        sid = supplier_service.create_supplier({'name': '测试供应商_005'})
        balance = supplier_service.get_supplier_payable(sid)
        self.assertEqual(balance, 0)

    def test_payable_balance_credit(self):
        """测试赊账采购后应付余额正确"""
        sid = supplier_service.create_supplier({'name': '测试供应商_006'})
        pid = product_service.create_product({'name': '测试产品_payable'})
        execute("INSERT INTO purchases (purchase_date, product_id, supplier_id, quantity, unit_price, total_amount, payment_type) VALUES ('2026-01-01', ?, ?, 10, 5, 50, 'credit')", (pid, sid))
        balance = supplier_service.get_supplier_payable(sid)
        self.assertEqual(balance, 50)
        # 列表查询也应包含应付余额
        suppliers = supplier_service.get_suppliers(keyword='测试供应商_006')
        self.assertEqual(suppliers[0]['payable_balance'], 50)
        # 清理
        execute("DELETE FROM purchases WHERE supplier_id = ?", (sid,))
        product_service.delete_product(pid)

    def test_search(self):
        supplier_service.create_supplier({'name': '测试供应商_搜索X'})
        results = supplier_service.get_suppliers(keyword='搜索X')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], '测试供应商_搜索X')


class TestCustomerService(unittest.TestCase):
    """测试客户服务层"""

    @classmethod
    def setUpClass(cls):
        execute("DELETE FROM customers WHERE name LIKE '测试客户_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM customers WHERE name LIKE '测试客户_%'")

    def test_create_and_get(self):
        cid = customer_service.create_customer({
            'name': '测试客户_001',
            'contact_person': '李四',
            'phone': '13700137000'
        })
        self.assertGreater(cid, 0)
        c = customer_service.get_customer_by_id(cid)
        self.assertEqual(c['name'], '测试客户_001')

    def test_update(self):
        cid = customer_service.create_customer({'name': '测试客户_002'})
        customer_service.update_customer(cid, {'name': '测试客户_002_改', 'address': '新地址'})
        c = customer_service.get_customer_by_id(cid)
        self.assertEqual(c['name'], '测试客户_002_改')
        self.assertEqual(c['address'], '新地址')

    def test_delete_no_ref(self):
        cid = customer_service.create_customer({'name': '测试客户_003'})
        success, msg = customer_service.delete_customer(cid)
        self.assertTrue(success)

    def test_delete_with_ref(self):
        cid = customer_service.create_customer({'name': '测试客户_004'})
        pid = product_service.create_product({'name': '测试产品_customer_ref'})
        execute("INSERT INTO sales (sale_date, product_id, customer_id, quantity, unit_price, total_amount, cost_amount, profit, payment_type) VALUES ('2026-01-01', ?, ?, 5, 10, 50, 25, 25, 'cash')", (pid, cid))
        success, msg = customer_service.delete_customer(cid)
        self.assertFalse(success)
        execute("DELETE FROM sales WHERE customer_id = ?", (cid,))
        product_service.delete_product(pid)
        customer_service.delete_customer(cid)

    def test_receivable_balance(self):
        cid = customer_service.create_customer({'name': '测试客户_005'})
        pid = product_service.create_product({'name': '测试产品_receivable'})
        execute("INSERT INTO sales (sale_date, product_id, customer_id, quantity, unit_price, total_amount, cost_amount, profit, payment_type) VALUES ('2026-01-01', ?, ?, 5, 10, 50, 25, 25, 'credit')", (pid, cid))
        balance = customer_service.get_customer_receivable(cid)
        self.assertEqual(balance, 50)
        execute("DELETE FROM sales WHERE customer_id = ?", (cid,))
        product_service.delete_product(pid)

    def test_search(self):
        customer_service.create_customer({'name': '测试客户_搜索Y'})
        results = customer_service.get_customers(keyword='搜索Y')
        self.assertEqual(len(results), 1)


class TestBaseDataRoutes(unittest.TestCase):
    """测试基础数据模块的路由API"""

    @classmethod
    def setUpClass(cls):
        from app import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        execute("DELETE FROM products WHERE name LIKE '路由测试_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '路由测试_%'")
        execute("DELETE FROM customers WHERE name LIKE '路由测试_%'")

    @classmethod
    def tearDownClass(cls):
        execute("DELETE FROM products WHERE name LIKE '路由测试_%'")
        execute("DELETE FROM suppliers WHERE name LIKE '路由测试_%'")
        execute("DELETE FROM customers WHERE name LIKE '路由测试_%'")

    def test_product_page_renders(self):
        resp = self.client.get('/products/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'\xe4\xba\xa7\xe5\x93\x81\xe4\xbf\xa1\xe6\x81\xaf', resp.data)

    def test_product_create_api(self):
        resp = self.client.post('/products/api/create', data={
            'name': '路由测试_产品1', 'category': '分类A', 'purchase_price': '10', 'sale_price': '15'
        })
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('id', data)

    def test_product_update_api(self):
        resp = self.client.post('/products/api/create', data={'name': '路由测试_产品2'})
        pid = resp.get_json()['id']
        resp2 = self.client.post(f'/products/api/update/{pid}', data={'name': '路由测试_产品2改'})
        self.assertTrue(resp2.get_json()['success'])

    def test_product_delete_api(self):
        resp = self.client.post('/products/api/create', data={'name': '路由测试_产品3'})
        pid = resp.get_json()['id']
        resp2 = self.client.post(f'/products/api/delete/{pid}')
        self.assertTrue(resp2.get_json()['success'])

    def test_supplier_create_api(self):
        resp = self.client.post('/suppliers/api/create', data={'name': '路由测试_供应商1'})
        self.assertTrue(resp.get_json()['success'])

    def test_customer_create_api(self):
        resp = self.client.post('/customers/api/create', data={'name': '路由测试_客户1'})
        self.assertTrue(resp.get_json()['success'])

    def test_empty_name_rejected(self):
        resp = self.client.post('/suppliers/api/create', data={'name': ''})
        self.assertFalse(resp.get_json()['success'])
        resp = self.client.post('/customers/api/create', data={'name': ''})
        self.assertFalse(resp.get_json()['success'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
