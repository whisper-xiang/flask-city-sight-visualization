# 城市景点可视化系统

基于Flask的城市景点数据可视化平台，整合多维度数据分析与可视化技术。

## 功能特性

- **多维度数据分析**: 评分、时间、空间、成本等多个维度分析景点特征
- **可视化展示**: 基于ECharts的丰富图表展示
- **地理分布**: 集成地图API展示景点空间分布
- **智能筛选**: 支持多条件筛选景点信息
- **用户系统**: 登录注册功能

## 技术栈

- **后端**: Flask + SQLAlchemy + MySQL
- **前端**: Bootstrap + ECharts + JavaScript
- **数据处理**: Pandas + NumPy
- **地图**: 百度地图API

## 项目结构

```
flask-city-sight-visualization/
├── app/                    # 应用核心代码
│   ├── __init__.py        # 应用初始化
│   ├── models.py          # 数据模型
│   ├── forms.py           # 表单定义
│   ├── views/             # 视图控制器
│   │   ├── auth.py        # 用户认证
│   │   ├── main.py        # 主要页面
│   │   ├── city.py        # 城市景点
│   │   └── dashboard.py   # 可视化大屏
│   └── utils/             # 工具函数
│       ├── data_analyzer.py    # 数据分析
│       └── data_processor.py   # 数据处理
├── config/                # 配置文件
├── static/                # 静态资源
├── templates/             # HTML模板
├── data/                  # 数据文件
├── requirements.txt       # 依赖包
└── run.py                # 启动文件
```

## 安装与运行

1. **克隆项目**
```bash
git clone <repository-url>
cd flask-city-sight-visualization
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

5. **初始化数据库**
```bash
python run.py
```

6. **访问应用**
打开浏览器访问: http://localhost:5000

## 数据导入

1. 将Kaggle数据集CSV文件放入 `data/` 目录
2. 运行数据导入脚本:
```python
from app.utils.data_processor import DataProcessor

processor = DataProcessor('data/china_city_attraction_details.csv')
df = processor.load_and_clean_data()
processor.save_to_database(df)
```

## 默认账户

- 用户名: admin
- 密码: admin123

## 开发说明

- 数据库表会在首次运行时自动创建
- 支持热重载开发模式
- 前端使用Bootstrap 5 + ECharts 5
- 后端API遵循RESTful设计

## 许可证

MIT License
