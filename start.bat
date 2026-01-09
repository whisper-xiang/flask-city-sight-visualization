@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========================================
:: Flask城市景点可视化系统 - 通用启动脚本
:: 版本: 2.0
:: 适用于Windows环境
:: ========================================

:: 设置颜色和标题
color 0A
title Flask城市景点可视化系统

:: 显示启动信息
echo.
echo ========================================
echo    Flask城市景点可视化系统启动器
echo ========================================
echo.

:: 检查Python是否安装
echo [1/6] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] Python版本: %PYTHON_VERSION%

:: 检查是否存在虚拟环境
echo.
echo [2/6] 检查虚拟环境...
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
)

:: 激活虚拟环境
echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)
echo [成功] 虚拟环境已激活

:: 升级pip
echo.
echo [3/6] 升级pip...
python -m pip install --upgrade pip >nul 2>&1

:: 安装依赖
echo [信息] 安装项目依赖...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [警告] 部分依赖安装失败，尝试继续...
    )
) else (
    echo [警告] 未找到requirements.txt文件
)

:: 检查环境配置文件
echo.
echo [4/6] 检查环境配置...
if not exist ".env" (
    echo [信息] 创建默认.env文件...
    (
        echo # 环境配置文件
        echo SECRET_KEY=fc840e680036a77ef5e90ce7018e1f169d0724dd24ddc7525a4db0705ab69a53
        echo FLASK_ENV=development
        echo DEBUG=True
        echo.
        echo # 数据库配置
        echo DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/city_attractions
        echo.
        echo # 百度地图API（可选）
        echo BAIDU_MAP_AK=
    ) > .env
    echo [成功] 已创建默认.env文件
)

:: 检查数据库连接
echo.
echo [5/6] 检查数据库连接...
python -c "import pymysql; print('PyMySQL已安装')" >nul 2>&1
if errorlevel 1 (
    echo [警告] PyMySQL未安装，尝试安装...
    pip install pymysql
)

:: 创建数据库表（如果需要）
echo [信息] 初始化数据库...
python -c "
try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
        print('[成功] 数据库表初始化完成')
except Exception as e:
    print(f'[警告] 数据库初始化失败: {e}')
    print('请检查数据库配置和连接')
"

:: 启动选项菜单
echo.
echo [6/6] 启动选项
echo ========================================
echo 1. 启动开发服务器 (默认)
echo 2. 启动调试模式
echo 3. 检查系统状态
echo 4. 退出
echo ========================================
set /p choice="请选择启动方式 (1-4，默认1): "

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo.
    echo [启动] 启动Flask开发服务器...
    echo [信息] 服务器地址: http://localhost:5001
    echo [信息] 按 Ctrl+C 停止服务器
    echo.
    python run.py
) else if "%choice%"=="2" (
    echo.
    echo [启动] 启动调试模式...
    echo [信息] 调试模式已启用
    echo [信息] 服务器地址: http://localhost:5001
    echo.
    set FLASK_DEBUG=1
    python run.py
) else if "%choice%"=="3" (
    echo.
    echo [检查] 系统状态检查...
    echo ========================================
    
    :: Python版本
    echo Python版本:
    python --version
    
    echo.
    echo 虚拟环境:
    if defined VIRTUAL_ENV (
        echo [激活] %VIRTUAL_ENV%
    ) else (
        echo [未激活] 虚拟环境未激活
    )
    
    echo.
    echo 关键依赖检查:
    for %%p in (flask sqlalchemy flask-login pandas numpy matplotlib) do (
        python -c "import %%p; print('  [OK] %%p')" 2>nul || echo "  [缺失] %%p"
    )
    
    echo.
    echo 数据库连接测试:
    python -c "
try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        from app.models import Attraction
        count = Attraction.query.count()
        print(f'  [成功] 数据库连接正常，景点数量: {count}')
except Exception as e:
    print(f'  [失败] 数据库连接失败: {e}')
"
    
    echo.
    echo 配置文件:
    if exist ".env" (
        echo [存在] .env文件
    ) else (
        echo [缺失] .env文件
    )
    
    echo ========================================
    echo.
    pause
    goto :start_menu
) else if "%choice%"=="4" (
    echo.
    echo [退出] 退出启动器
    goto :end
) else (
    echo [错误] 无效选择，使用默认选项
    echo.
    echo [启动] 启动Flask开发服务器...
    python run.py
)

:start_menu
echo.
echo 是否重新选择启动选项？(Y/N)
set /p retry="请输入选择: "
if /i "%retry%"=="Y" goto :start
if /i "%retry%"=="y" goto :start

:end
echo.
echo [完成] 感谢使用Flask城市景点可视化系统！
echo.
pause