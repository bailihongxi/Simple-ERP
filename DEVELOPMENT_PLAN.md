# 个人进销存系统 - 开发计划

> 基于 PRD.md v1.0 制定。按阶段顺序执行，每个阶段完成并验证后再进入下一阶段。

---

## 一、技术栈

| 层级 | 选型 | 说明 |
|------|------|------|
| 后端 | Python 3 + Flask | 轻量本地服务，零配置 |
| 数据库 | SQLite3 | Python 内置，单文件存储 |
| 前端 | Jinja2 模板 + 原生 HTML/CSS/JS | 不引入前端框架，减少依赖，直接渲染 |
| Excel | openpyxl | 导入导出 .xlsx |
| 启动 | .command 脚本（Mac） | 双击启动，自动打开浏览器 |

**为什么不用前端框架**：个人本地工具，页面交互不复杂，原生 JS + 服务端渲染足够，减少构建工具和依赖，降低维护成本。

---

## 二、项目目录结构

```
ERP/
├── PRD.md                    # 需求文档（已有）
├── DEVELOPMENT_PLAN.md       # 本开发计划
├── requirements.txt          # Python 依赖
├── app.py                    # Flask 主入口，注册路由、启动服务
├── start.command             # Mac 启动脚本（双击运行）
│
├── database/
│   ├── __init__.py
│   ├── db.py                 # 数据库连接、初始化建表、通用查询函数
│   └── schema.sql            # 建表 SQL 语句
│
├── routes/                   # 各模块路由（蓝图）
│   ├── __init__.py
│   ├── dashboard.py          # 首页总览
│   ├── products.py           # 产品信息
│   ├── suppliers.py          # 供应商信息
│   ├── customers.py          # 客户信息
│   ├── purchase.py           # 采购管理
│   ├── sales.py              # 销售管理
│   ├── inventory.py          # 库存管理
│   ├── finance.py            # 财务信息
│   └── backup.py             # 备份恢复
│
├── services/                 # 业务逻辑层（路由调用，避免路由里写复杂 SQL）
│   ├── __init__.py
│   ├── product_service.py
│   ├── supplier_service.py
│   ├── customer_service.py
│   ├── purchase_service.py
│   ├── sales_service.py
│   ├── inventory_service.py
│   ├── finance_service.py
│   └── backup_service.py
│
├── utils/
│   ├── __init__.py
│   ├── excel.py              # Excel 导入导出通用工具
│   └── helpers.py            # 日期格式化、金额格式化等通用函数
│
├── templates/                # Jinja2 模板
│   ├── base.html             # 基础布局：左侧导航 + 顶部栏 + 内容区
│   ├── dashboard.html
│   ├── products.html
│   ├── suppliers.html
│   ├── customers.html
│   ├── purchase.html
│   ├── sales.html
│   ├── inventory.html
│   ├── finance.html
│   └── backup.html           # 备份恢复管理页（可放在设置弹窗里）
│
├── static/
│   ├── css/
│   │   └── style.css         # 全局样式
│   └── js/
│       └── app.js            # 全局 JS（弹窗、表单提交、筛选等通用交互）
│
├── data/
│   └── erp_data.db           # 数据库文件（首次启动自动创建，git 忽略）
│
└── backups/                  # 备份文件目录（git 忽略）
```

---

## 三、数据库表设计

### 3.1 products（产品表）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 产品ID |
| name | TEXT | NOT NULL | 商品名称 |
| category | TEXT | | 分类 |
| unit | TEXT | | 单位（个/箱/斤） |
| purchase_price | REAL | DEFAULT 0 | 进货价 |
| sale_price | REAL | DEFAULT 0 | 售价 |
| current_stock | REAL | DEFAULT 0 | 当前库存（由系统维护，不可手动改） |
| avg_cost | REAL | DEFAULT 0 | 加权平均成本（由采购自动计算维护） |
| default_supplier_id | INTEGER | | 默认供应商ID |
| warning_stock | REAL | DEFAULT 0 | 低库存预警值 |
| notes | TEXT | | 备注 |
| created_at | TEXT | | 创建时间 |
| updated_at | TEXT | | 更新时间 |

### 3.2 suppliers（供应商表）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 供应商ID |
| name | TEXT | NOT NULL | 供应商名称 |
| contact_person | TEXT | | 联系人 |
| phone | TEXT | | 电话 |
| address | TEXT | | 地址 |
| notes | TEXT | | 备注 |
| created_at | TEXT | | 创建时间 |

> 应付余额不存字段，通过采购赊账金额 - 已付款金额实时计算。

### 3.3 customers（客户表）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 客户ID |
| name | TEXT | NOT NULL | 客户名称 |
| contact_person | TEXT | | 联系人 |
| phone | TEXT | | 电话 |
| address | TEXT | | 地址 |
| notes | TEXT | | 备注 |
| created_at | TEXT | | 创建时间 |

> 应收余额不存字段，通过销售赊账金额 - 已收款金额实时计算。

### 3.4 purchases（采购记录表）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 采购记录ID |
| purchase_date | TEXT | NOT NULL | 采购日期（YYYY-MM-DD） |
| product_id | INTEGER | NOT NULL | 商品ID |
| supplier_id | INTEGER | | 供应商ID |
| quantity | REAL | NOT NULL | 数量 |
| unit_price | REAL | NOT NULL | 单价 |
| total_amount | REAL | NOT NULL | 总金额（数量×单价） |
| payment_type | TEXT | NOT NULL DEFAULT 'cash' | 付款方式：cash现结 / credit赊账 |
| notes | TEXT | | 备注 |
| created_at | TEXT | | 创建时间 |

### 3.5 sales（销售记录表）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 销售记录ID |
| sale_date | TEXT | NOT NULL | 销售日期 |
| product_id | INTEGER | NOT NULL | 商品ID |
| customer_id | INTEGER | | 客户ID |
| quantity | REAL | NOT NULL | 数量 |
| unit_price | REAL | NOT NULL | 单价 |
| total_amount | REAL | NOT NULL | 总金额 |
| cost_amount | REAL | NOT NULL | 成本金额（保存时取商品进货价×数量） |
| profit | REAL | NOT NULL | 毛利（total_amount - cost_amount） |
| payment_type | TEXT | NOT NULL DEFAULT 'cash' | 收款方式：cash现结 / credit赊账 |
| notes | TEXT | | 备注 |
| created_at | TEXT | | 创建时间 |

### 3.6 inventory_adjustments（库存盘点调整表）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 调整记录ID |
| product_id | INTEGER | NOT NULL | 商品ID |
| adjust_date | TEXT | NOT NULL | 调整日期 |
| old_stock | REAL | NOT NULL | 调整前库存 |
| new_stock | REAL | NOT NULL | 调整后库存 |
| change_amount | REAL | NOT NULL | 变动量（new - old） |
| reason | TEXT | | 调整原因 |
| notes | TEXT | | 备注 |
| created_at | TEXT | | 创建时间 |

### 3.7 payments（收付款记录表）
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 记录ID |
| payment_date | TEXT | NOT NULL | 日期 |
| type | TEXT | NOT NULL | receive收款 / pay付款 |
| party_type | TEXT | NOT NULL | customer / supplier |
| party_id | INTEGER | NOT NULL | 客户ID或供应商ID |
| amount | REAL | NOT NULL | 金额 |
| notes | TEXT | | 备注 |
| created_at | TEXT | | 创建时间 |

### 3.8 库存变动流水（不单独建表，通过视图/联合查询实现）
库存变动流水从三张表联合查询：
- purchases → 类型"采购入库"，变动量 = +quantity
- sales → 类型"销售出库"，变动量 = -quantity
- inventory_adjustments → 类型"盘点调整"，变动量 = change_amount

按时间倒序排列，关联商品名称。

---

## 四、分阶段开发计划

### 阶段 0：项目初始化与骨架搭建

**目标**：项目能跑起来，浏览器能看到一个带左侧导航的空白页面框架，数据库自动创建。

**任务**：

1. 创建目录结构（database/、routes/、services/、utils/、templates/、static/css/、static/js/、data/、backups/）
2. 写 `requirements.txt`：Flask、openpyxl
3. 写 `database/schema.sql`：7 张表的建表语句
4. 写 `database/db.py`：
   - 数据库连接函数（每次请求连接，请求结束关闭）
   - 初始化函数：执行 schema.sql，不存在则创建
   - 通用查询封装：query_all、query_one、execute
5. 写 `app.py`：
   - 创建 Flask app
   - 注册所有蓝图（先注册空蓝图）
   - 启动时调用数据库初始化
   - 运行在 0.0.0.0:5000，debug=True
6. 写 `templates/base.html`：
   - 左侧导航栏（8 个菜单项，高亮当前页）
   - 顶部标题栏
   - 内容区 {% block content %}
   - 引入 style.css 和 app.js
7. 写 `static/css/style.css`：
   - 全局重置、左侧导航样式、内容区布局、表格基础样式、按钮样式、弹窗样式
8. 写 `static/js/app.js`：
   - 通用弹窗函数（showModal / hideModal）
   - 确认删除对话框
   - 表单 AJAX 提交通用函数
9. 每个模块写一个最小路由 + 空白模板，确保 8 个页面都能打开切换
10. 写 `start.command`：cd 到项目目录，python3 app.py，然后自动 open http://localhost:5000

**完成标志**：
- 终端运行 `python3 app.py` 无报错
- 浏览器打开 http://localhost:5000 看到首页框架
- 左侧 8 个导航都能点击，页面切换正常
- data/ 目录下自动生成 erp_data.db
- 用 sqlite 工具查看，7 张表都已创建

---

### 阶段 1：基础数据模块（产品、供应商、客户）

**目标**：三个基础档案模块的增删改查全部完成，能正常录入和管理基础数据。

**1.1 产品信息模块**

路由文件 `routes/products.py`，服务文件 `services/product_service.py`，模板 `templates/products.html`。

任务：
1. 产品列表页：表格显示所有产品（名称、分类、单位、进货价、售价、当前库存、预警值、默认供应商、操作）
2. 搜索筛选：按名称模糊搜索、按分类筛选
3. 新增产品：弹窗表单（名称必填、分类、单位、进货价、售价、预警值、默认供应商下拉、备注）
4. 编辑产品：弹窗表单，回显已有数据
5. 删除产品：
   - 先检查是否有关联的采购或销售记录
   - 有关联则提示"该产品有采购/销售记录，无法删除"
   - 无关联则删除，二次确认
6. 服务层封装：get_products、get_product_by_id、create_product、update_product、delete_product、check_product_references

**1.2 供应商信息模块**

路由 `routes/suppliers.py`，服务 `services/supplier_service.py`，模板 `templates/suppliers.html`。

任务：
1. 供应商列表：名称、联系人、电话、地址、应付余额、操作
   - 应付余额 = 该供应商赊账采购总额 - 已付款总额（SQL 联合查询计算）
2. 搜索：按名称模糊搜索
3. 新增/编辑：弹窗表单（名称必填、联系人、电话、地址、备注）
4. 删除：检查是否有关联采购记录，有则不可删除
5. 服务层封装，含应付余额计算函数

**1.3 客户信息模块**

路由 `routes/customers.py`，服务 `services/customer_service.py`，模板 `templates/customers.html`。

任务：
1. 客户列表：名称、联系人、电话、地址、应收余额、操作
   - 应收余额 = 该客户赊账销售总额 - 已收款总额
2. 搜索：按名称模糊搜索
3. 新增/编辑：弹窗表单
4. 删除：检查是否有关联销售记录，有则不可删除
5. 服务层封装，含应收余额计算函数

**完成标志**：
- 能新增、编辑、删除（无关联的）产品/供应商/客户
- 列表显示正确，搜索筛选有效
- 有关联记录的产品删除时弹出提示，不删除
- 供应商应付余额、客户应收余额暂时为 0（因为还没做采购销售）

---

### 阶段 2：采购管理模块

**目标**：采购记录的增删改查完成，新增采购自动增加库存、赊账自动增加应付。

路由 `routes/purchase.py`，服务 `services/purchase_service.py`，模板 `templates/purchase.html`。

任务：
1. 采购列表：日期、商品名称、供应商名称、数量、单价、总金额、付款方式（现结/赊账标签）、备注、操作
2. 筛选：日期范围（开始日期-结束日期）、供应商下拉、商品名称搜索
3. 新增采购：弹窗表单
   - 采购日期（默认今天）
   - 商品下拉（从 products 表加载，显示名称）
   - 供应商下拉（从 suppliers 表加载）
   - 数量、单价（数字输入）
   - 总金额自动计算（JS 实时计算：数量×单价）
   - 付款方式：单选（现结/赊账，默认现结）
   - 备注
   - 提交后服务端：
     a. 插入采购记录
     b. 更新 products.current_stock += quantity
     c. 更新加权平均成本：avg_cost = (old_stock × old_avg_cost + quantity × unit_price) ÷ (old_stock + quantity)；old_stock 为 0 时 avg_cost = unit_price
     d. 如果是赊账，应付余额自动体现（因为是实时计算的，不需要额外操作）
4. 编辑采购：弹窗表单回显
   - 提交后服务端：
     a. 计算新旧数量差：delta = 新数量 - 旧数量
     b. 更新 products.current_stock += delta
     c. 重新计算该商品加权平均成本：按时间顺序遍历该商品所有采购记录，逐次计算平均成本
     d. 更新采购记录其他字段
     e. 付款方式变更不影响库存，但影响应付计算（实时计算自动体现）
5. 删除采购：二次确认
   - 服务端：
     a. 更新 products.current_stock -= 采购数量
     b. 删除采购记录
     c. 重新计算该商品加权平均成本（遍历剩余采购记录，按时间顺序重算）
6. 采购统计：页面顶部显示当前筛选条件下的采购总金额、采购笔数
7. 服务层封装，所有写操作使用数据库事务（保证库存和记录同步）

**关键技术点**：
- 写操作必须用事务：BEGIN → 插入/更新采购 → 更新库存 → COMMIT，出错则 ROLLBACK
- 编辑时要先查出旧记录的数量，计算差值再更新库存

**完成标志**：
- 新增一条现结采购，产品库存增加，供应商应付不变
- 新增一条赊账采购，产品库存增加，供应商应付余额增加
- 编辑采购数量，库存同步变化
- 删除采购，库存回退
- 筛选功能正常
- 采购总金额统计正确

---

### 阶段 3：销售管理模块

**目标**：销售记录的增删改查完成，新增销售自动减少库存、赊账自动增加应收、自动计算成本和毛利。

路由 `routes/sales.py`，服务 `services/sales_service.py`，模板 `templates/sales.html`。

任务：
1. 销售列表：日期、商品名称、客户名称、数量、单价、总金额、成本金额、毛利、收款方式、备注、操作
2. 筛选：日期范围、客户下拉、商品名称搜索
3. 新增销售：弹窗表单
   - 销售日期（默认今天）
   - 商品下拉
   - 客户下拉
   - 数量、单价
   - 总金额 JS 自动计算
   - 收款方式：现结/赊账
   - 备注
   - 提交后服务端：
     a. 查出商品当前加权平均成本 avg_cost
     b. cost_amount = avg_cost × quantity
     c. profit = (unit_price × quantity) - cost_amount
     d. 插入销售记录（含 cost_amount、profit）
     e. 更新 products.current_stock -= quantity
     f. 赊账则应收余额自动体现（实时计算）
   - 库存不足提示：如果 current_stock < quantity，提示"库存不足，当前库存 X"，阻止提交
4. 编辑销售：
   - 服务端：
     a. 查出旧记录
     b. delta = 新数量 - 旧数量
     c. 更新 products.current_stock -= delta（注意是减 delta，因为销售是减库存）
     d. 重新计算 cost_amount 和 profit（用当前商品加权平均成本；编辑销售不改变平均成本，只更新本次销售的成本记录）
     e. 更新销售记录
5. 删除销售：
   - 服务端：products.current_stock += 销售数量，然后删除记录
6. 销售统计：当前筛选下的销售总金额、总成本、总毛利、销售笔数
7. 服务层事务封装

**完成标志**：
- 新增现结销售，库存减少，客户应收不变，毛利正确
- 新增赊账销售，库存减少，客户应收增加
- 库存不足时无法销售，有提示
- 编辑销售，库存、成本、毛利同步更新
- 删除销售，库存回加
- 销售统计金额正确

---

### 阶段 4：库存管理模块

**目标**：库存列表、低库存预警、盘点功能、库存变动流水。

路由 `routes/inventory.py`，服务 `services/inventory_service.py`，模板 `templates/inventory.html`。

任务：
1. 库存列表：商品名称、分类、单位、当前库存、成本价（加权平均成本）、库存价值（当前库存×加权平均成本）、预警值、状态
   - 状态：current_stock <= warning_stock 则"低库存"标红，否则"正常"
2. 筛选：按分类筛选、按商品名称搜索、只看低库存（复选框）
3. 盘点功能：
   - 每行有"盘点"按钮，点击弹窗
   - 显示当前库存，输入新库存，填写调整原因
   - 提交后服务端：
     a. 查出当前库存 old_stock
     b. change_amount = new_stock - old_stock
     c. 插入 inventory_adjustments 记录
     d. 更新 products.current_stock = new_stock
     e. 事务保证
4. 库存变动流水：
   - 页面有"变动记录"标签页或弹窗
   - 联合查询 purchases、sales、inventory_adjustments
   - 字段：时间、类型（采购入库/销售出库/盘点调整）、商品、变动数量（正数绿色+、负数红色-）、变动后库存、备注
   - 按时间倒序
   - 可按商品筛选
5. 库存汇总：页面顶部显示商品种类数、库存总数量、库存总价值、低库存商品数

**完成标志**：
- 库存列表数据正确，低库存标红
- 盘点后库存更新，变动流水出现盘点记录
- 变动流水能看到采购、销售、盘点的所有记录
- 库存价值计算正确

---

### 阶段 5：应收应付（收付款）

**目标**：供应商付款、客户收款功能完成，收付款记录可查。

这部分功能放在供应商和客户模块里，同时财务模块也会读取。

任务：
1. 供应商详情/付款：
   - 在供应商列表每行加"付款"按钮
   - 弹窗显示：供应商名称、当前应付余额、付款金额输入、付款日期、备注
   - 提交后插入 payments 表（type='pay', party_type='supplier'）
   - 应付余额自动减少（实时计算体现）
   - 供应商详情弹窗中显示付款历史列表
2. 客户详情/收款：
   - 客户列表每行加"收款"按钮
   - 弹窗显示：客户名称、当前应收余额、收款金额输入、收款日期、备注
   - 提交后插入 payments 表（type='receive', party_type='customer'）
   - 应收余额自动减少
   - 客户详情弹窗中显示收款历史列表
3. 供应商历史采购记录：在供应商详情弹窗中显示该供应商的所有采购记录
4. 客户历史销售记录：在客户详情弹窗中显示该客户的所有销售记录

**完成标志**：
- 给供应商付款后，应付余额减少
- 客户收款后，应收余额减少
- 能查看供应商的采购历史和付款历史
- 能查看客户的销售历史和收款历史

---

### 阶段 6：财务信息模块

**目标**：收支利润汇总、应收应付总览、收付款记录列表、按月趋势。

路由 `routes/finance.py`，服务 `services/finance_service.py`，模板 `templates/finance.html`。

任务：
1. 时间段选择器：开始日期、结束日期（默认本月）
2. 汇总卡片：
   - 总收入 = 时间段内现结销售总额 + 时间段内收款总额
   - 总支出 = 时间段内现结采购总额 + 时间段内付款总额
   - 毛利 = 时间段内销售记录的 profit 之和
   - 毛利率 = 毛利 / 销售总金额 × 100%
3. 应收应付总览：
   - 应收账款总额 = 所有客户应收余额之和
   - 应付账款总额 = 所有供应商应付余额之和
4. 收付款记录列表：
   - 日期、类型（收款/付款）、对方名称、金额、备注
   - 按类型筛选（全部/收款/付款）
   - 按日期倒序
5. 按月趋势：
   - 最近 6 个月的收入、支出、毛利柱状图（用纯 CSS 画简易柱状图，不引入图表库）
   - 或用表格展示每月数据
6. 服务层封装所有统计查询

**完成标志**：
- 切换时间段，汇总数字正确变化
- 收入 = 现结销售 + 收款，支出 = 现结采购 + 付款
- 毛利与销售模块的毛利合计一致
- 收付款记录与供应商/客户模块的记录一致

---

### 阶段 7：首页总览

**目标**：数据看板完成，所有指标正确显示，快捷跳转可用。

路由 `routes/dashboard.py`，服务层调用各模块 service，模板 `templates/dashboard.html`。

任务：
1. 第一排指标卡片：今日进货金额、今日销售金额、本月毛利、库存总价值
2. 第二排指标卡片：本月进货金额/笔数、本月销售金额/笔数、应收总额、应付总额
3. 低库存预警列表：
   - 查询 current_stock <= warning_stock 的产品
   - 显示商品名称、当前库存、预警值、分类
   - 点击跳转到产品页（可带搜索参数）
4. 近期交易记录：
   - 联合查询最近 10 条采购和销售记录
   - 用 UNION 合并，按时间倒序
   - 显示：时间、类型标签（采购蓝/销售绿）、商品、数量、金额、对方
5. 快捷操作按钮：「快速进货」→ /purchase?action=new，「快速销售」→ /sales?action=new
   - 对应页面检测到 action=new 参数时自动打开新增弹窗
6. 所有数据从各 service 层获取，不重复写 SQL

**完成标志**：
- 所有指标数字与各模块数据一致
- 低库存列表与库存模块一致
- 近期记录按时间倒序，最近 10 条
- 点击快捷按钮跳转到对应页面并打开新增表单
- 点击预警商品跳转到产品页

---

### 阶段 8：Excel 导入导出

**目标**：所有模块支持导出，基础数据和交易记录支持导入。

工具文件 `utils/excel.py`，各模块路由中添加导入导出端点。

任务：
1. 写通用 Excel 工具：
   - export_to_excel(headers, rows, filename)：生成 .xlsx 文件返回下载
   - import_from_excel(file)：解析 .xlsx 返回字典列表
2. 产品模块：
   - 导出：所有产品字段导出为 Excel
   - 导入：读取 Excel，按名称匹配，存在则更新、不存在则新增
   - 导入模板下载：提供空模板（含表头）
3. 供应商模块：导出 + 导入 + 模板
4. 客户模块：导出 + 导入 + 模板
5. 采购模块：
   - 导出：当前筛选条件下的采购记录导出
   - 导入：导入采购记录，导入时自动触发库存增加和应付处理（复用 create_purchase 逻辑）
6. 销售模块：
   - 导出：当前筛选条件下的销售记录导出
   - 导入：导入销售记录，自动触发库存减少、应收处理、成本和毛利计算
7. 库存模块：导出当前库存表
8. 财务模块：导出当前时间段的财务汇总和收付款记录
9. 每个模块页面加"导出"按钮和"导入"按钮（导入弹窗，可下载模板）

**完成标志**：
- 每个模块都能导出 Excel，打开后数据正确
- 产品/供应商/客户能从 Excel 导入，导入后列表正确
- 采购/销售导入后，库存和应收应付同步变化
- 导入模板下载可用

---

### 阶段 9：备份与恢复

**目标**：一键备份、从备份恢复、备份列表管理。

路由 `routes/backup.py`，服务 `services/backup_service.py`，可以放在一个"数据管理"弹窗或单独页面。

任务：
1. 备份功能：
   - 复制 data/erp_data.db 到 backups/backup_YYYYMMDD_HHMMSS.db
   - 用 shutil.copy2 保留文件元信息
   - 备份时数据库可能有连接，使用 SQLite 的 backup API 或先确保没有写入
2. 备份列表：
   - 扫描 backups/ 目录下所有 .db 文件
   - 显示文件名、备份时间（从文件名解析或文件修改时间）、文件大小
   - 按时间倒序
3. 恢复功能：
   - 选择一个备份文件，点击恢复
   - 恢复前先自动备份当前数据到 backups/backup_before_restore_时间戳.db
   - 然后用备份文件覆盖 data/erp_data.db
   - 提示用户刷新页面
4. 删除备份：可以删除不需要的备份文件（二次确认）
5. 在顶部导航栏加"数据管理"入口（或设置图标），打开备份管理弹窗
6. 启动时自动备份（可选，配置项控制）：每次启动服务时自动备份一份

**完成标志**：
- 点击备份，backups/ 目录生成带时间戳的 .db 文件
- 备份列表显示所有备份
- 恢复后数据变为备份时的状态，且当前数据被自动备份
- 能删除备份文件

---

### 阶段 10：整体测试与优化

**目标**：全流程跑通，修复 bug，优化体验。

任务：
1. 全流程测试（按 PRD 第 10 章验收标准逐条验证）：
   - 启动测试
   - 产品/供应商/客户增删改查
   - 采购全流程（新增/编辑/删除/库存联动/应付联动）
   - 销售全流程（新增/编辑/删除/库存联动/应收联动/毛利）
   - 库存盘点和变动流水
   - 收付款
   - 财务汇总
   - 首页指标
   - Excel 导入导出
   - 备份恢复
   - 数据一致性校验
2. 边界情况处理：
   - 数量为 0 或负数的校验
   - 金额为负数的校验
   - 删除有依赖数据的提示
   - 库存不足销售的提示
   - 导入 Excel 格式错误的提示
   - 日期格式校验
3. 用户体验优化：
   - 表单输入即时校验
   - 操作成功/失败提示（toast 提示）
   - 列表分页（数据多时）
   - 数字格式化（金额保留 2 位小数，千分位）
   - 空状态提示（列表为空时显示"暂无数据"）
4. 样式优化：
   - 响应式布局（窗口缩放不错乱）
   - 统一的配色和间距
   - 表格斑马纹、hover 效果
5. 启动脚本完善：
   - start.command 检查 Python3 是否安装
   - 检查依赖是否安装，未安装则自动 pip install
   - 启动后自动打开浏览器
   - 终端显示访问地址和退出提示

**完成标志**：
- PRD 第 10 章所有验收项全部通过
- 无明显 bug
- 操作流畅，提示清晰

---

## 五、开发顺序说明

```
阶段0 骨架 → 阶段1 基础数据 → 阶段2 采购 → 阶段3 销售
     → 阶段4 库存 → 阶段5 收付款 → 阶段6 财务 → 阶段7 首页
     → 阶段8 Excel → 阶段9 备份 → 阶段10 测试
```

**为什么这个顺序**：
1. 先搭骨架，确保技术路线通
2. 先做基础数据（产品/供应商/客户），因为后续模块都要引用它们
3. 采购和销售是核心业务，做完后库存自动有数据
4. 库存盘点依赖已有库存数据
5. 收付款依赖已有赊账记录
6. 财务依赖采购、销售、收付款数据
7. 首页依赖所有模块的数据，所以最后做
8. Excel 和备份是辅助功能，主体功能完成后再加
9. 最后统一测试

---

## 六、关键技术约定

### 6.1 日期格式
- 统一使用 `YYYY-MM-DD` 字符串存储
- 显示时格式化为 `YYYY年MM月DD日`
- 时间戳使用 `YYYY-MM-DD HH:MM:SS`

### 6.2 金额处理
- 数据库存 REAL 类型
- 显示时保留 2 位小数，加千分位（如 1,234.56）
- 计算时注意浮点数精度，必要时用 round(x, 2)

### 6.3 数据库事务
所有涉及多表写入的操作（采购/销售/盘点/收付款）必须使用事务：
```python
conn = get_db()
try:
    conn.execute('BEGIN')
    # 多步写入
    conn.execute('COMMIT')
except Exception:
    conn.execute('ROLLBACK')
    raise
```

### 6.4 库存与成本计算原则
- products.current_stock 是权威字段，由系统维护
- 每次采购 +quantity，每次销售 -quantity，盘点直接设值
- 不通过实时聚合计算当前库存（性能考虑）
- 库存变动流水通过联合查询展示
- **加权平均成本（avg_cost）**：
  - 新增采购时更新：avg_cost = (原库存 × 原平均成本 + 采购数量 × 采购单价) ÷ (原库存 + 采购数量)
  - 原库存为 0 时，直接取本次采购单价
  - 销售不改变平均成本，只减少库存数量和库存总价值
  - 编辑/删除采购记录后，重新遍历该商品所有采购记录按时间顺序重算平均成本
  - 销售成本在销售时按当时的 avg_cost 计算并固化到 sales.cost_amount，后续不回溯修改历史销售
  - 库存总价值 = current_stock × avg_cost

### 6.5 应收应付计算原则
- 不存冗余字段，实时计算：
  - 供应商应付 = SUM(赊账采购金额) - SUM(已付款金额)
  - 客户应收 = SUM(赊账销售金额) - SUM(已收款金额)
- 列表页通过 SQL 联合查询一次算出，避免 N+1 查询

### 6.6 前端交互
- 新增/编辑用弹窗（Modal），不跳页
- 表单通过 AJAX 提交（fetch API），成功后刷新列表区域
- 删除二次确认
- 操作结果用 toast 提示（成功绿色、失败红色）

---

## 七、风险与注意事项

1. **SQLite 并发**：单用户本地使用，不存在并发问题，但写操作仍要用事务保证一致性
2. **库存为负**：销售时必须检查库存，不足则阻止；盘点允许调整为任意值
3. **删除约束**：产品/供应商/客户有关联记录时不可删除，只能编辑或标记停用（第一版不做停用，直接禁止删除）
4. **成本精度**：销售成本按销售时的加权平均成本计算并固化到销售记录；编辑/删除历史采购会重算当前平均成本但不回溯修改历史销售的成本，可能导致微小差异，个人使用可接受
5. **Excel 导入容错**：导入时逐行校验，出错行跳过并报告，不整体失败
6. **备份时数据库锁定**：备份操作应在无写入时进行，或使用 SQLite online backup API

---

*计划版本：v1.0*
*创建日期：2026-08-11*
*基于 PRD 版本：v1.0*
