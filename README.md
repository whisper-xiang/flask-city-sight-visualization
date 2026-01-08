# 城市景点可视化系统

基于 Flask 的城市景点信息可视化平台，提供景点数据展示、搜索、评价等功能。

## 首次启动步骤

### 方法一：一键启动（推荐）

**macOS/Linux 用户：**
```bash
chmod +x start.sh
./start.sh
```

**Windows 用户：**
```cmd
start.bat
```

### 方法二：手动启动

#### 1. 环境准备

**检查 Python 版本：**
- 需要 Python 3.12（推荐）或 3.11
- 检查命令：`python3.12 --version` 或 `python3.11 --version`

**安装 Python（如未安装）：**

**Windows:**
- 访问 https://www.python.org/downloads/ 下载 Python 3.12
- 安装时勾选 "Add Python to PATH"

**macOS:**
- `brew install python@3.12`

**Linux:**
- Ubuntu/Debian: `sudo apt install python3.12 python3.12-venv`
- CentOS/RHEL: `sudo dnf install python3.12`

#### 2. 创建虚拟环境

```bash
# 使用检测到的 Python 版本创建虚拟环境
python3.12 -m venv venv  # 或 python3.11 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
# 升级构建工具
python -m pip install --upgrade pip setuptools wheel

# 安装项目依赖
pip install -r requirements.txt
```

#### 4. 数据库配置

**启动 MySQL 服务：**

**Windows:**
- 方法一：使用服务管理器启动 MySQL 服务
- 方法二：命令行启动 `net start mysql`
- 方法三：使用 XAMPP/WAMP 等集成环境启动 MySQL

**macOS (Homebrew):**
```bash
brew services start mysql
```

**创建数据库：**
**Windows 命令行（如果 MySQL 在 PATH 中）：**
```cmd
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS city_attractions CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```


#### 6. 初始化数据库表

```bash
python -c "
from app import create_app, db
from app.models import Attraction, Review, Favorite, User
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print('数据库表初始化完成')
"
```

#### 7. 导入数据

```bash
# 导入数据（使用找到的文件）
python import_data.py data/cleaned_attractions.csv
```

#### 8. 启动应用

```bash
python run.py
```

访问 http://localhost:5000 查看应用。

## 项目结构

```
flask-city-sight-visualization/
├── app/                    # 应用主目录
│   ├── models/            # 数据模型
│   ├── utils/             # 工具函数
│   ├── views/             # 视图控制器
│   ├── forms.py           # 表单定义
│   └── models.py          # 数据模型
├── config/                # 配置文件
├── data/                  # 数据文件
├── static/                # 静态资源
├── templates/             # 模板文件
├── start.sh              # macOS/Linux 启动脚本
├── start.bat             # Windows 启动脚本
├── requirements.txt      # Python 依赖
└── run.py               # 应用入口
```

## 功能特性

- 🏙️ 城市景点信息展示
- 🔍 景点搜索与筛选
- ⭐ 用户评价与收藏
- 📊 数据可视化分析
- 📱 响应式设计

## 开发环境

- Python 3.12/3.11
- Flask
- MySQL
- Bootstrap/Tailwind CSS

## 许可证

MIT License