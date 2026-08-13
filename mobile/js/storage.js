// ==================== localStorage 数据存储封装 ====================
const STORAGE_PREFIX = 'SimpleERP_';

/**
 * 初始化存储
 */
function initStorage() {
    return new Promise((resolve, reject) => {
        try {
            // 检查 localStorage 是否可用
            const testKey = STORAGE_PREFIX + 'test';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            resolve();
        } catch (e) {
            reject(e);
        }
    });
}

/**
 * 保存数据到指定存储
 * @param {string} storeName - 存储名称
 * @param {Array} data - 数据数组
 */
function saveData(storeName, data) {
    return new Promise((resolve, reject) => {
        try {
            localStorage.setItem(STORAGE_PREFIX + storeName, JSON.stringify(data));
            resolve();
        } catch (e) {
            reject(e);
        }
    });
}

/**
 * 从指定存储读取数据
 * @param {string} storeName - 存储名称
 * @returns {Promise<Array>} 数据数组
 */
function getData(storeName) {
    return new Promise((resolve, reject) => {
        try {
            const data = localStorage.getItem(STORAGE_PREFIX + storeName);
            resolve(data ? JSON.parse(data) : []);
        } catch (e) {
            reject(e);
        }
    });
}

/**
 * 清除所有数据
 */
function clearAllData() {
    return new Promise((resolve, reject) => {
        try {
            const stores = ['products', 'purchases', 'sales', 'suppliers', 'customers', 'meta'];
            stores.forEach(store => {
                localStorage.removeItem(STORAGE_PREFIX + store);
            });
            resolve();
        } catch (e) {
            reject(e);
        }
    });
}

/**
 * 设置元数据
 * @param {string} key - 键
 * @param {*} value - 值
 */
function setMeta(key, value) {
    return new Promise((resolve, reject) => {
        try {
            const meta = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'meta') || '{}');
            meta[key] = value;
            localStorage.setItem(STORAGE_PREFIX + 'meta', JSON.stringify(meta));
            resolve();
        } catch (e) {
            reject(e);
        }
    });
}

/**
 * 获取元数据
 * @param {string} key - 键
 * @returns {Promise<*>} 值
 */
function getMeta(key) {
    return new Promise((resolve, reject) => {
        try {
            const meta = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'meta') || '{}');
            resolve(meta[key] !== undefined ? meta[key] : null);
        } catch (e) {
            reject(e);
        }
    });
}

/**
 * 导入数据（全量覆盖）
 * @param {Object} data - 完整的数据对象
 */
function importData(data) {
    return new Promise(async (resolve, reject) => {
        try {
            // 校验必要字段
            if (!data.products || !data.purchases || !data.sales) {
                throw new Error('数据格式不正确，缺少必要字段');
            }

            // 清除旧数据
            await clearAllData();

            // 写入新数据
            await saveData('products', data.products || []);
            await saveData('purchases', data.purchases || []);
            await saveData('sales', data.sales || []);
            await saveData('suppliers', data.suppliers || []);
            await saveData('customers', data.customers || []);

            // 写入元数据
            if (data.export_time) {
                await setMeta('import_time', data.export_time);
            }
            if (data.version) {
                await setMeta('version', data.version);
            }

            resolve({
                product_count: (data.products || []).length,
                purchase_count: (data.purchases || []).length,
                sale_count: (data.sales || []).length
            });
        } catch (e) {
            reject(e);
        }
    });
}
