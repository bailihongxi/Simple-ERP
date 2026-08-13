// ==================== 全局变量 ====================
let currentTab = 'home';
let pageHistory = ['home'];
let allProducts = [];
let allPurchases = [];
let allSales = [];

// ==================== 工具函数 ====================
function showToast(msg, duration = 2000) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, duration);
}

function showConfirm(title, message, onConfirm) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = message;
    document.getElementById('modalOverlay').style.display = 'flex';
    document.getElementById('modalConfirmBtn').onclick = function() {
        closeModal();
        if (onConfirm) onConfirm();
    };
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
}

function fmtMoney(n) {
    if (n === null || n === undefined || isNaN(n)) return '0.00';
    return parseFloat(n).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function fmtNum(n) {
    if (n === null || n === undefined || isNaN(n)) return '0';
    const num = parseFloat(n);
    if (Number.isInteger(num)) return num.toString();
    return num.toFixed(2);
}

// ==================== 页面切换 ====================
const pageTitles = {
    home: '进销存',
    products: '产品信息',
    sales: '销售记录',
    inventory: '库存查询',
    purchase: '采购记录',
    mine: '我的'
};

function switchTab(tab) {
    currentTab = tab;
    pageHistory = [tab];

    // 更新底部导航
    document.querySelectorAll('.tab-item').forEach(item => {
        item.classList.toggle('active', item.dataset.tab === tab);
    });

    // 更新顶部栏
    updateTopbar(tab);

    // 切换页面
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + tab).classList.add('active');

    // 加载数据
    loadPageData(tab);
}

function updateTopbar(tab) {
    document.getElementById('topbarTitle').textContent = pageTitles[tab] || '进销存';

    // 首页显示设置按钮，隐藏返回按钮
    if (tab === 'home') {
        document.getElementById('backBtn').style.display = 'none';
        document.getElementById('settingsBtn').style.display = 'flex';
    } else {
        document.getElementById('settingsBtn').style.display = 'none';
        // 底部导航的页面（products, sales）不显示返回按钮
        if (['products', 'sales'].includes(tab)) {
            document.getElementById('backBtn').style.display = 'none';
        } else {
            document.getElementById('backBtn').style.display = 'flex';
        }
    }
}

function goBack() {
    if (pageHistory.length > 1) {
        pageHistory.pop();
        const prevPage = pageHistory[pageHistory.length - 1];
        currentTab = prevPage;
        updateTopbar(prevPage);
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById('page-' + prevPage).classList.add('active');
        loadPageData(prevPage);
    } else {
        switchTab('home');
    }
}

function goToSettings() {
    navigateTo('mine');
}

function goToInventory() {
    navigateTo('inventory');
}

function goToPurchase() {
    navigateTo('purchase');
}

function navigateTo(page) {
    pageHistory.push(page);
    currentTab = page;
    updateTopbar(page);
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');
    loadPageData(page);
}

function loadPageData(page) {
    switch(page) {
        case 'home':
            loadHomeData();
            break;
        case 'products':
            loadProducts();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'purchase':
            loadPurchases();
            break;
        case 'sales':
            loadSales();
            break;
        case 'mine':
            loadMine();
            break;
    }
}

// ==================== 首页 ====================
async function loadHomeData() {
    allProducts = await getData('products');
    // 首页不需要加载数据，搜索时才用
}

function handleSearch() {
    const keyword = document.getElementById('searchInput').value.trim().toLowerCase();
    const container = document.getElementById('searchResults');

    if (!keyword) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div class="empty-text">输入关键词搜索产品</div>
            </div>`;
        return;
    }

    const results = allProducts.filter(p =>
        (p.name || '').toLowerCase().includes(keyword)
    );

    if (results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div class="empty-text">未找到相关产品</div>
            </div>`;
        return;
    }

    container.innerHTML = results.map(p => {
        const isLow = parseFloat(p.warning_stock || 0) > 0 && parseFloat(p.current_stock || 0) <= parseFloat(p.warning_stock || 0);
        return `
        <div class="list-item">
            <div class="item-title">${p.name || '-'}</div>
            <div class="item-meta">
                <span>${p.brand || '-'}</span>
                <span>${p.category || '-'}</span>
            </div>
            <div class="item-meta">
                <span>进货价：¥${fmtMoney(p.purchase_price)}</span>
                <span>售价：¥${fmtMoney(p.sale_price)}</span>
            </div>
            <div class="item-meta">
                <span>库存：<span class="${isLow ? 'low-stock' : ''}">${fmtNum(p.current_stock)} ${p.unit || ''}</span></span>
            </div>
            ${isLow ? '<div class="item-tags"><span class="tag tag-red">低库存</span></div>' : ''}
        </div>`;
    }).join('');
}

// ==================== 产品模块 ====================
async function loadProducts() {
    allProducts = await getData('products');
    allProducts.sort((a, b) => b.id - a.id);

    // 填充品牌和分类下拉
    populateBrandCategory('productBrand', 'productCategory', allProducts);

    renderProducts(allProducts);
}

function populateBrandCategory(brandId, catId, products) {
    const brands = [...new Set(products.map(p => p.brand).filter(b => b))].sort();
    const cats = [...new Set(products.map(p => p.category).filter(c => c))].sort();

    const brandSelect = document.getElementById(brandId);
    const currentBrand = brandSelect.value;
    brandSelect.innerHTML = '<option value="">全部品牌</option>';
    brands.forEach(b => {
        brandSelect.innerHTML += `<option value="${b}">${b}</option>`;
    });
    brandSelect.value = currentBrand;

    const catSelect = document.getElementById(catId);
    const currentCat = catSelect.value;
    catSelect.innerHTML = '<option value="">全部分类</option>';
    cats.forEach(c => {
        catSelect.innerHTML += `<option value="${c}">${c}</option>`;
    });
    catSelect.value = currentCat;
}

function renderProducts(products) {
    const container = document.getElementById('productList');
    if (products.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <div class="empty-text">暂无产品数据</div>
            </div>`;
        return;
    }

    container.innerHTML = products.map(p => {
        const isLow = parseFloat(p.warning_stock || 0) > 0 && parseFloat(p.current_stock || 0) <= parseFloat(p.warning_stock || 0);
        return `
        <div class="list-item">
            <div class="item-title">${p.name || '-'}</div>
            <div class="item-meta">
                <span>${p.brand || '-'}</span>
                <span>${p.category || '-'}</span>
            </div>
            <div class="item-meta">
                <span>进货价：¥${fmtMoney(p.purchase_price)}</span>
                <span>售价：¥${fmtMoney(p.sale_price)}</span>
            </div>
            <div class="item-meta">
                <span>库存：<span class="${isLow ? 'low-stock' : ''}">${fmtNum(p.current_stock)} ${p.unit || ''}</span></span>
                ${isLow ? '<span class="tag tag-red">低库存</span>' : ''}
            </div>
        </div>`;
    }).join('');
}

function filterProducts() {
    const brand = document.getElementById('productBrand').value;
    const category = document.getElementById('productCategory').value;

    let filtered = allProducts;
    if (brand) {
        filtered = filtered.filter(p => p.brand === brand);
    }
    if (category) {
        filtered = filtered.filter(p => p.category === category);
    }
    renderProducts(filtered);
}

function resetProductFilter() {
    document.getElementById('productBrand').value = '';
    document.getElementById('productCategory').value = '';
    renderProducts(allProducts);
}

// ==================== 库存模块 ====================
async function loadInventory() {
    allProducts = await getData('products');
    allProducts.sort((a, b) => b.id - a.id);

    // 计算统计
    const totalProducts = allProducts.length;
    const totalStock = allProducts.reduce((sum, p) => sum + parseFloat(p.current_stock || 0), 0);
    const totalValue = allProducts.reduce((sum, p) => sum + parseFloat(p.current_stock || 0) * parseFloat(p.avg_cost || 0), 0);
    const lowStock = allProducts.filter(p => parseFloat(p.warning_stock || 0) > 0 && parseFloat(p.current_stock || 0) <= parseFloat(p.warning_stock || 0)).length;

    document.getElementById('invTotalProducts').textContent = totalProducts;
    document.getElementById('invTotalStock').textContent = fmtNum(totalStock);
    document.getElementById('invTotalValue').textContent = '¥' + fmtMoney(totalValue);
    document.getElementById('invLowStock').textContent = lowStock;

    populateBrandCategory('invBrand', 'invCategory', allProducts);
    renderInventory(allProducts);
}

function renderInventory(items) {
    const container = document.getElementById('inventoryList');
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <div class="empty-text">暂无库存数据</div>
            </div>`;
        return;
    }

    container.innerHTML = items.map(p => {
        const isLow = parseFloat(p.warning_stock || 0) > 0 && parseFloat(p.current_stock || 0) <= parseFloat(p.warning_stock || 0);
        const stockValue = parseFloat(p.current_stock || 0) * parseFloat(p.avg_cost || 0);
        return `
        <div class="list-item">
            <div class="item-title">${p.name || '-'}</div>
            <div class="item-meta">
                <span>${p.brand || '-'}</span>
                <span>${p.category || '-'}</span>
            </div>
            <div class="item-meta">
                <span>当前库存：<span class="${isLow ? 'low-stock' : ''}">${fmtNum(p.current_stock)} ${p.unit || ''}</span></span>
                <span>均价：¥${fmtMoney(p.avg_cost)}</span>
            </div>
            <div class="item-meta">
                <span>库存价值：¥${fmtMoney(stockValue)}</span>
                <span>${isLow ? '<span class="tag tag-red">低库存</span>' : '<span class="tag tag-green">正常</span>'}</span>
            </div>
        </div>`;
    }).join('');
}

function filterInventory() {
    const keyword = document.getElementById('invKeyword').value.toLowerCase();
    const brand = document.getElementById('invBrand').value;
    const category = document.getElementById('invCategory').value;
    const lowOnly = document.getElementById('invLowOnly').checked;

    let filtered = allProducts;
    if (keyword) {
        filtered = filtered.filter(p => (p.name || '').toLowerCase().includes(keyword));
    }
    if (brand) {
        filtered = filtered.filter(p => p.brand === brand);
    }
    if (category) {
        filtered = filtered.filter(p => p.category === category);
    }
    if (lowOnly) {
        filtered = filtered.filter(p => parseFloat(p.warning_stock || 0) > 0 && parseFloat(p.current_stock || 0) <= parseFloat(p.warning_stock || 0));
    }
    renderInventory(filtered);
}

function resetInventoryFilter() {
    document.getElementById('invKeyword').value = '';
    document.getElementById('invBrand').value = '';
    document.getElementById('invCategory').value = '';
    document.getElementById('invLowOnly').checked = false;
    renderInventory(allProducts);
}

// ==================== 采购模块 ====================
async function loadPurchases() {
    allPurchases = await getData('purchases');
    allPurchases.sort((a, b) => {
        if (a.purchase_date !== b.purchase_date) return b.purchase_date.localeCompare(a.purchase_date);
        return b.id - a.id;
    });

    // 统计
    const count = allPurchases.length;
    const total = allPurchases.reduce((sum, p) => sum + parseFloat(p.total_amount || 0), 0);

    document.getElementById('purCount').textContent = count;
    document.getElementById('purTotal').textContent = '¥' + fmtMoney(total);

    renderPurchases(allPurchases);

    // 更新产品页的快捷入口数据
    if (document.getElementById('quickPurTotal')) {
        document.getElementById('quickPurTotal').textContent = '¥' + fmtMoney(total);
    }
}

function renderPurchases(items) {
    const container = document.getElementById('purchaseList');
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📥</div>
                <div class="empty-text">暂无采购记录</div>
            </div>`;
        return;
    }

    container.innerHTML = items.map(p => `
        <div class="list-item">
            <div class="item-title">${p.product_name || '-'}</div>
            <div class="item-meta">
                <span>${p.purchase_date || '-'}</span>
                <span class="money">¥${fmtMoney(p.total_amount)}</span>
            </div>
            <div class="item-meta">
                <span>供应商：${p.supplier_name || '-'}</span>
                <span>数量：${fmtNum(p.quantity)}</span>
            </div>
            <div class="item-meta">
                <span>单价：¥${fmtMoney(p.unit_price)}</span>
                <span>${p.payment_type === 'credit' ? '<span class="tag tag-orange">赊账</span>' : '<span class="tag tag-green">现结</span>'}</span>
            </div>
        </div>
    `).join('');
}

function filterPurchases() {
    const dateStart = document.getElementById('purDateStart').value;
    const dateEnd = document.getElementById('purDateEnd').value;
    const keyword = document.getElementById('purKeyword').value.toLowerCase();

    let filtered = allPurchases;
    if (dateStart) {
        filtered = filtered.filter(p => p.purchase_date >= dateStart);
    }
    if (dateEnd) {
        filtered = filtered.filter(p => p.purchase_date <= dateEnd);
    }
    if (keyword) {
        filtered = filtered.filter(p =>
            (p.product_name || '').toLowerCase().includes(keyword) ||
            (p.supplier_name || '').toLowerCase().includes(keyword)
        );
    }
    renderPurchases(filtered);
}

function resetPurchaseFilter() {
    document.getElementById('purDateStart').value = '';
    document.getElementById('purDateEnd').value = '';
    document.getElementById('purKeyword').value = '';
    renderPurchases(allPurchases);
}

// ==================== 销售模块 ====================
async function loadSales() {
    allSales = await getData('sales');
    allSales.sort((a, b) => {
        if (a.sale_date !== b.sale_date) return b.sale_date.localeCompare(a.sale_date);
        return b.id - a.id;
    });

    // 统计
    const count = allSales.length;
    const total = allSales.reduce((sum, s) => sum + parseFloat(s.total_amount || 0), 0);
    const cost = allSales.reduce((sum, s) => sum + parseFloat(s.cost_amount || 0), 0);
    const profit = allSales.reduce((sum, s) => sum + parseFloat(s.profit || 0), 0);

    document.getElementById('saleCount').textContent = count;
    document.getElementById('saleTotal').textContent = '¥' + fmtMoney(total);
    document.getElementById('saleCost').textContent = '¥' + fmtMoney(cost);
    document.getElementById('saleProfit').textContent = '¥' + fmtMoney(profit);
    document.getElementById('saleProfit').className = 'stat-value ' + (profit >= 0 ? 'green' : 'red');

    renderSales(allSales);
}

function renderSales(items) {
    const container = document.getElementById('salesList');
    if (items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📤</div>
                <div class="empty-text">暂无销售记录</div>
            </div>`;
        return;
    }

    container.innerHTML = items.map(s => {
        const profit = parseFloat(s.profit || 0);
        return `
        <div class="list-item">
            <div class="item-title">${s.product_name || '-'}</div>
            <div class="item-meta">
                <span>${s.sale_date || '-'}</span>
                <span class="money">¥${fmtMoney(s.total_amount)}</span>
            </div>
            <div class="item-meta">
                <span>客户：${s.customer_name || '-'}</span>
                <span>数量：${fmtNum(s.quantity)}</span>
            </div>
            <div class="item-meta">
                <span>单价：¥${fmtMoney(s.unit_price)}</span>
                <span>${s.payment_type === 'credit' ? '<span class="tag tag-orange">赊账</span>' : '<span class="tag tag-green">现结</span>'}</span>
            </div>
            <div class="item-meta">
                <span>成本：¥${fmtMoney(s.cost_amount)}</span>
                <span class="money" style="color:${profit >= 0 ? '#16a34a' : '#dc2626'}">毛利：¥${fmtMoney(profit)}</span>
            </div>
        </div>`;
    }).join('');
}

function filterSales() {
    const dateStart = document.getElementById('saleDateStart').value;
    const dateEnd = document.getElementById('saleDateEnd').value;
    const keyword = document.getElementById('saleKeyword').value.toLowerCase();

    let filtered = allSales;
    if (dateStart) {
        filtered = filtered.filter(s => s.sale_date >= dateStart);
    }
    if (dateEnd) {
        filtered = filtered.filter(s => s.sale_date <= dateEnd);
    }
    if (keyword) {
        filtered = filtered.filter(s =>
            (s.product_name || '').toLowerCase().includes(keyword) ||
            (s.customer_name || '').toLowerCase().includes(keyword)
        );
    }
    renderSales(filtered);
}

function resetSaleFilter() {
    document.getElementById('saleDateStart').value = '';
    document.getElementById('saleDateEnd').value = '';
    document.getElementById('saleKeyword').value = '';
    renderSales(allSales);
}

// ==================== 我的/设置模块 ====================
async function loadMine() {
    const products = await getData('products');
    const purchases = await getData('purchases');
    const sales = await getData('sales');
    const importTime = await getMeta('import_time');

    const container = document.getElementById('dataSummary');
    if (products.length === 0 && purchases.length === 0 && sales.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <div class="empty-text">暂无数据，请先导入数据</div>
            </div>`;
    } else {
        const totalValue = products.reduce((sum, p) => sum + parseFloat(p.current_stock || 0) * parseFloat(p.avg_cost || 0), 0);
        const purchaseTotal = purchases.reduce((sum, p) => sum + parseFloat(p.total_amount || 0), 0);
        container.innerHTML = `
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-item-value">${products.length}</div>
                    <div class="summary-item-label">商品</div>
                </div>
                <div class="summary-item">
                    <div class="summary-item-value">${purchases.length}</div>
                    <div class="summary-item-label">采购</div>
                </div>
                <div class="summary-item">
                    <div class="summary-item-value">${sales.length}</div>
                    <div class="summary-item-label">销售</div>
                </div>
            </div>
            <div class="summary-extra">
                库存总价值：¥${fmtMoney(totalValue)}<br>
                采购总金额：¥${fmtMoney(purchaseTotal)}<br>
                ${importTime ? '数据导入时间：' + importTime : ''}
            </div>
        `;
    }
}

function triggerImport() {
    document.getElementById('importFile').click();
}

async function handleImport(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
        showToast('请选择 JSON 格式的数据文件');
        event.target.value = '';
        return;
    }

    try {
        const text = await file.text();
        const data = JSON.parse(text);

        if (!data.products || !data.purchases || !data.sales) {
            showToast('文件格式不正确，缺少必要数据');
            event.target.value = '';
            return;
        }

        const productCount = data.summary?.product_count || data.products.length;
        const purchaseCount = data.summary?.purchase_count || data.purchases.length;
        const saleCount = data.summary?.sale_count || data.sales.length;

        showConfirm(
            '确认导入数据？',
            `即将导入以下数据：<br><br>商品：${productCount} 条<br>采购：${purchaseCount} 条<br>销售：${saleCount} 条<br><br><strong style="color:#dc2626;">导入后将覆盖现有全部数据！</strong>`,
            async function() {
                try {
                    showToast('正在导入...', 500);
                    await importData(data);
                    showToast('导入成功！');
                    event.target.value = '';
                    // 刷新数据
                    allProducts = await getData('products');
                    allPurchases = await getData('purchases');
                    allSales = await getData('sales');
                    loadPageData(currentTab);
                } catch (e) {
                    showToast('导入失败：' + e.message);
                    event.target.value = '';
                }
            }
        );
    } catch (e) {
        showToast('导入失败：' + e.message);
        event.target.value = '';
    }
}

function clearAllData() {
    showConfirm(
        '确认清除数据？',
        '<strong style="color:#dc2626;">此操作将清除所有本地数据，不可恢复！</strong><br><br>确定要继续吗？',
        async function() {
            try {
                await clearAllData();
                showToast('数据已清除');
                allProducts = [];
                allPurchases = [];
                allSales = [];
                loadPageData(currentTab);
            } catch (e) {
                showToast('清除失败：' + e.message);
            }
        }
    );
}

// ==================== 初始化 ====================
async function init() {
    try {
        await initStorage();
        allProducts = await getData('products');
        allPurchases = await getData('purchases');
        allSales = await getData('sales');
        switchTab('home');
    } catch (e) {
        console.error('初始化失败', e);
        showToast('初始化失败：' + e.message);
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
