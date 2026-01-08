from app import db
from datetime import datetime
from flask_login import UserMixin

class Attraction(db.Model):
    __tablename__ = 'attractions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    link = db.Column(db.String(500))
    address = db.Column(db.String(500))
    description = db.Column(db.Text)
    opening_hours = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float)
    recommended_duration = db.Column(db.String(50))
    recommended_season = db.Column(db.Text)
    ticket_price = db.Column(db.Text)
    tips = db.Column(db.Text)
    province = db.Column(db.String(50), index=True)
    city = db.Column(db.String(50), index=True)
    district = db.Column(db.String(500), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name or '未命名景点',
            'link': self.link,
            'address': self.address,
            'description': self.description,
            'opening_hours': self.opening_hours,
            'image_url': self.image_url,
            'rating': self.rating or 0,
            'recommended_duration': self.recommended_duration or '暂无信息',
            'recommended_season': self.recommended_season or '暂无信息',
            'ticket_price': self.ticket_price or '暂无信息',
            'tips': self.tips,
            'province': self.province or '未知',
            'city': self.city or '未知',
            'district': self.district,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1-5星评分
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user = db.relationship('User', backref=db.backref('reviews', lazy=True, cascade='all, delete-orphan'))
    attraction = db.relationship('Attraction', backref=db.backref('reviews', lazy=True, cascade='all, delete-orphan'))
    
    # 确保同一用户对同一景点只能评价一次
    __table_args__ = (db.UniqueConstraint('user_id', 'attraction_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'attraction_id': self.attraction_id,
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'username': self.user.username if self.user else '匿名用户'
            }
        }

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    user = db.relationship('User', backref=db.backref('favorites', lazy=True, cascade='all, delete-orphan'))
    attraction = db.relationship('Attraction', backref=db.backref('favorites', lazy=True, cascade='all, delete-orphan'))
    
    # 确保同一用户不能重复收藏同一景点
    __table_args__ = (db.UniqueConstraint('user_id', 'attraction_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'attraction_id': self.attraction_id,
            'attraction': self.attraction.to_dict() if self.attraction else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
