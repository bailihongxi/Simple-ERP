#!/bin/bash
cd "$(dirname "$0")"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 Python3，请先安装 Python 3.8+"
    read -p "按回车键退出..."
    exit 1
fi

# 检查并安装依赖
if ! python3 -c "import flask" &> /dev/null; then
    echo "正在安装依赖..."
    python3 -m pip install -r requirements.txt
fi

echo "启动进销存管理系统..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
python3 app.py
