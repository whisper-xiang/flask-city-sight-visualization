@echo off
REM 一键启动脚本（Windows）
REM 包含：MySQL检查、建库、建表、导入数据、启动Flask

echo 🚀 城市景点可视化系统 - 一键启动脚本

REM 1. 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 2. 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 确保构建工具可用（避免: Cannot import 'setuptools.build_meta'）
python -m pip install -q --upgrade pip setuptools wheel

REM 3. 安装依赖
echo 📚 安装依赖...
pip install -q -r requirements.txt

REM 4. 检查 MySQL 服务（Windows）
sc query mysql 2>nul | find "RUNNING" >nul
if errorlevel 1 (
    echo 🗄️ 尝试启动 MySQL 服务...
    net start mysql
    timeout /t 3 >nul
) else (
    echo ✅ MySQL 服务已运行
)

REM 5. 处理 .env
if not exist ".env" (
    copy .env.example .env >nul
)

REM 检查 SECRET_KEY 是否为默认值
findstr /C:"dev-secret-key-change-in-production" .env >nul
if not errorlevel 1 (
    echo 🔑 生成新的 SECRET_KEY...
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_hex())"') do set SECRET_KEY=%%i
    powershell -Command "(Get-Content .env) -replace 'SECRET_KEY=.*', 'SECRET_KEY=%SECRET_KEY%' | Set-Content .env"
)

REM 6. 创建数据库（如果不存在）
echo 🗃️ 检查/创建数据库...
set DB_NAME=city_attractions
set DB_USER=root
set DB_PASS=password

mysql -u%DB_USER% -p%DB_PASS% -e "USE %DB_NAME%;" 2>nul
if errorlevel 1 (
    echo 📝 创建数据库 %DB_NAME%...
    mysql -u%DB_USER% -p%DB_PASS% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
) else (
    echo ✅ 数据库 %DB_NAME% 已存在
)

REM 7. 初始化表
echo 🧱 初始化数据库表...
python -c "from app import create_app, db; from app.models import Attraction, Review, Favorite, User; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all(); print('✅ 数据库表初始化完成')"

REM 8. 导入数据（如果 data/ 目录有 CSV）
if exist "data\cleaned_attractions.csv" (
    echo 📥 发现清洗后的数据文件，开始导入...
    python import_data.py data/cleaned_attractions.csv
) else if exist "data\attractions_export.csv" (
    echo 📥 发现导出数据文件，开始导入...
    python import_data.py data/attractions_export.csv
) else if exist "data\china_city_attraction_details.csv" (
    echo 📥 发现原始数据文件，开始导入...
    python import_data.py data/china_city_attraction_details.csv
) else (
    echo ℹ️ 未发现可用的 CSV 数据文件，跳过导入
)

REM 9. 启动 Flask
echo 🌐 启动 Flask 服务...
set FLASK_ENV=development
set FLASK_APP=run.py

echo.
echo 🎉 启动完成！访问: http://localhost:5000
echo.
python run.py
pause
