from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config.config import config

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def format_rating(rating):
    """格式化评分为星级显示"""
    if not rating:
        return "暂无评分"
    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    return stars

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[config_name])
    
    # 添加模板函数
    app.jinja_env.globals['format_rating'] = format_rating
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    
    # 注册蓝图
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.city import city_bp
    from app.views.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(city_bp, url_prefix='/city')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    return app
