import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/city_attractions'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }
    
    # 百度地图API配置
    BAIDU_MAP_AK = os.environ.get('BAIDU_MAP_AK') or ''
    
    # 数据文件路径
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    RAW_DATA_FILE = os.path.join(DATA_DIR, 'china_city_attraction_details.csv')
    
    # 分页配置
    ATTRACTIONS_PER_PAGE = 20

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
