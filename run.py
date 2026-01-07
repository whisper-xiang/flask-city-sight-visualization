from app import create_app, db
from app.models import User, Attraction

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 创建数据库表
        db.create_all()
        print("数据库表创建完成")
        
        # 创建默认管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("默认管理员用户创建完成: admin/admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
