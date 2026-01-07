from app import db
from datetime import datetime

class Attraction(db.Model):
    __tablename__ = 'attractions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    link = db.Column(db.String(500))
    address = db.Column(db.String(500))
    description = db.Column(db.Text)
    opening_hours = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float)
    recommended_duration = db.Column(db.String(50))
    recommended_season = db.Column(db.String(50))
    ticket_price = db.Column(db.String(100))
    tips = db.Column(db.Text)
    province = db.Column(db.String(50), index=True)
    city = db.Column(db.String(50), index=True)
    district = db.Column(db.String(50), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'link': self.link,
            'address': self.address,
            'description': self.description,
            'opening_hours': self.opening_hours,
            'image_url': self.image_url,
            'rating': self.rating,
            'recommended_duration': self.recommended_duration,
            'recommended_season': self.recommended_season,
            'ticket_price': self.ticket_price,
            'tips': self.tips,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

class User(db.Model):
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
