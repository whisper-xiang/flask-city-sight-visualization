#!/bin/bash

# 一键启动脚本（macOS/Linux）
# 包含：MySQL检查/启动、建库、建表、导入数据、启动Flask

set -e

echo "🚀 城市景点可视化系统 - 一键启动脚本"

# 1. 检查 Python 环境（优先 python3.12，其次 python3.11）
PYTHON_CMD=""
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
else
    echo "❌ 未找到 python3.12 / python3.11，请先安装 Python 3.12（推荐）或 3.11"
    echo "💡 macOS 安装命令: brew install python@3.12"
    echo "💡 Ubuntu/Debian 安装命令: sudo apt install python3.12 python3.12-venv"
    echo "💡 CentOS/RHEL 安装命令: sudo dnf install python3.12"
    exit 1
fi

echo "🐍 使用 Python: $(${PYTHON_CMD} --version)"

# 2. 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    ${PYTHON_CMD} -m venv venv
fi

echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 确保构建工具可用（避免: Cannot import 'setuptools.build_meta'）
python -m pip install -q --upgrade pip setuptools wheel

# 3. 安装依赖
echo "📚 安装依赖..."
pip install -q -r requirements.txt

# 4. 检查/启动 MySQL
if command -v brew &> /dev/null; then
    # macOS with Homebrew
    if ! brew services list | grep mysql | grep started &> /dev/null; then
        echo "🗄️ 启动 MySQL（Homebrew）..."
        brew services start mysql
        sleep 3
    fi
elif command -v systemctl &> /dev/null; then
    # Linux with systemd
    if ! systemctl is-active --quiet mysql; then
        echo "🗄️ 启动 MySQL（systemd）..."
        sudo systemctl start mysql
        sleep 3
    fi
else
    echo "⚠️ 无法自动启动 MySQL，请确保 MySQL 已运行"
fi

# 5. 生成 SECRET_KEY（如果 .env 里没有）
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

if ! grep -q "SECRET_KEY=" .env || grep -q "dev-secret-key-change-in-production" .env; then
    echo "🔑 生成新的 SECRET_KEY..."
    SECRET_KEY=$(${PYTHON_CMD} -c "import secrets; print(secrets.token_hex())")
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
fi

# 6. 创建数据库（如果不存在）
echo "🗃️ 检查/创建数据库..."
DB_NAME="city_attractions"
DB_USER="root"
DB_PASS=""

# 检查 MySQL 连接
if mysql -u"${DB_USER}" -p"${DB_PASS}" -e "USE ${DB_NAME};" 2>/dev/null; then
    echo "✅ 数据库 ${DB_NAME} 已存在"
else
    echo "📝 创建数据库 ${DB_NAME}..."
    mysql -u"${DB_USER}" -p"${DB_PASS}" -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
fi

# 7. 初始化表
echo "🧱 初始化数据库表..."
${PYTHON_CMD} -c "
from app import create_app, db
from app.models import Attraction, Review, Favorite, User
app = create_app()
with app.app_context():
    # 删除所有表以重新创建（应用新的schema）
    db.drop_all()
    db.create_all()
    print('✅ 数据库表初始化完成')
"

# 8. 导入数据（如果 data/ 目录有 CSV）
if [ -f "data/cleaned_attractions.csv" ]; then
    echo "📥 发现清洗后的数据文件，开始导入..."
    ${PYTHON_CMD} import_data.py data/cleaned_attractions.csv
elif [ -f "data/attractions_export.csv" ]; then
    echo "📥 发现导出数据文件，开始导入..."
    ${PYTHON_CMD} import_data.py data/attractions_export.csv
elif [ -f "data/china_city_attraction_details.csv" ]; then
    echo "📥 发现原始数据文件，开始导入..."
    ${PYTHON_CMD} import_data.py data/china_city_attraction_details.csv
else
    echo "ℹ️ 未发现可用的 CSV 数据文件，跳过导入"
fi

# 9. 启动 Flask
echo "🌐 启动 Flask 服务..."
export FLASK_ENV=development
export FLASK_APP=run.py

echo "🎉 启动完成！访问: http://localhost:5000"
${PYTHON_CMD} run.py
