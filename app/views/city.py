from flask import Blueprint, render_template, request, jsonify
from app.models import Attraction
from app.utils.data_analyzer import DataAnalyzer

city_bp = Blueprint('city', __name__)

@city_bp.route('/')
def city_index():
    return render_template('city/index.html')

@city_bp.route('/attractions')
def attractions():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 筛选参数
    province = request.args.get('province')
    city = request.args.get('city')
    rating_min = request.args.get('rating_min', type=float)
    season = request.args.get('season')
    is_free = request.args.get('is_free')
    
    # 构建查询
    query = Attraction.query
    
    if province:
        query = query.filter(Attraction.province == province)
    if city:
        query = query.filter(Attraction.city == city)
    if rating_min:
        query = query.filter(Attraction.rating >= rating_min)
    if season:
        query = query.filter(Attraction.recommended_season == season)
    if is_free == '1':
        query = query.filter(Attraction.ticket_price == '免费')
    
    attractions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('city/attractions.html', attractions=attractions)

@city_bp.route('/attraction/<int:id>')
def attraction_detail(id):
    attraction = Attraction.query.get_or_404(id)
    return render_template('city/attraction_detail.html', attraction=attraction)

@city_bp.route('/api/provinces')
def get_provinces():
    provinces = db.session.query(Attraction.province).distinct().all()
    return jsonify([p[0] for p in provinces if p[0]])

@city_bp.route('/api/cities')
def get_cities():
    province = request.args.get('province')
    query = db.session.query(Attraction.city).distinct()
    if province:
        query = query.filter(Attraction.province == province)
    cities = query.all()
    return jsonify([c[0] for c in cities if c[0]])
