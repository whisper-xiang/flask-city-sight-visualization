# Flask 城市景点可视化系统

一个基于 Flask 的中国城市景点数据分析和可视化平台，提供景点信息展示、数据统计分析和用户交互功能。

## 📋 系统要求

- Python 3.8+
- MySQL 5.7+
- Windows/Linux/macOS

## 🛠️ 安装与运行

### 方法一：使用启动脚本（推荐）

#### Windows 用户

```bash
# 完整功能启动器（包含虚拟环境激活、依赖安装、数据库初始化）以管理员身份运行，或者在编辑器下打开终端输入：
./start.bat

```

### 方法二：手动安装

1. **创建虚拟环境**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **初始化数据库**

```bash
python run.py
```

## 🌐 访问地址

- **主页**: http://localhost:5001
- **景点列表**: http://localhost:5001/city/attractions
- **数据仪表板**: http://localhost:5001/dashboard
- **用户登录**: http://localhost:5001/auth/login

## 📊 数据说明

项目包含 352 个中国城市的景点数据，涵盖：

- **基本信息**: 名称、地址、描述、开放时间
- **评价信息**: 评分、用户评价
- **实用信息**: 门票价格、推荐游玩时长、推荐季节
- **地理信息**: 省份、城市、区域、经纬度坐标

## 🎯 使用指南

### 1. 启动应用

运行启动脚本后，访问 http://localhost:5001

## 🐛 故障排除

### 常见问题

#### 1. MySQL 连接失败

```bash
# 检查MySQL服务状态
net start mysql

# 创建数据库
mysql -u root -p -e "CREATE DATABASE city_attractions;"
```

#### 2. 依赖安装失败

```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt


```

#### 3. 端口占用

```bash
# 修改run.py中的端口
app.run(debug=True, host='0.0.0.0', port=5002)
```

**注意**: 首次运行会自动创建数据库表和默认管理员账户（admin/admin123）
