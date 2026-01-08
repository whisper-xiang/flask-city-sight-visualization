from flask import Blueprint, render_template, jsonify, request
from app import db
from app.models import Attraction
from app.utils.data_analyzer import DataAnalyzer

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    return render_template('dashboard/index.html')

@dashboard_bp.route('/api/statistics')
def get_statistics():
    analyzer = DataAnalyzer()
    stats = analyzer.get_all_statistics()
    return jsonify(stats)

@dashboard_bp.route('/api/rating-distribution')
def rating_distribution():
    analyzer = DataAnalyzer()
    data = analyzer.get_rating_distribution()
    return jsonify(data)

@dashboard_bp.route('/api/season-distribution')
def season_distribution():
    analyzer = DataAnalyzer()
    data = analyzer.get_season_distribution()
    return jsonify(data)

@dashboard_bp.route('/api/rating-duration-correlation')
def rating_duration_correlation():
    analyzer = DataAnalyzer()
    data = analyzer.get_rating_duration_correlation()
    return jsonify(data)

@dashboard_bp.route('/api/province-distribution')
def province_distribution():
    analyzer = DataAnalyzer()
    data = analyzer.get_province_distribution()
    return jsonify(data)

@dashboard_bp.route('/api/city-distribution')
def city_distribution():
    analyzer = DataAnalyzer()
    data = analyzer.get_city_distribution()
    return jsonify(data)

@dashboard_bp.route('/api/geo-distribution')
def geo_distribution():
    analyzer = DataAnalyzer()
    data = analyzer.get_geo_distribution()
    return jsonify(data)

@dashboard_bp.route('/api/price-distribution')
def price_distribution():
    analyzer = DataAnalyzer()
    data = analyzer.get_price_distribution()
    return jsonify(data)

@dashboard_bp.route('/api/duration-distribution')
def duration_distribution():
    analyzer = DataAnalyzer()
    data = analyzer.get_duration_distribution()
    return jsonify(data)

@dashboard_bp.route('/api/top-attractions')
def top_attractions():
    analyzer = DataAnalyzer()
    data = analyzer.get_top_attractions()
    return jsonify(data)

@dashboard_bp.route('/data')
def data_table():
    """数据表格页面"""
    return render_template('dashboard/data.html')

@dashboard_bp.route('/api/data')
def get_table_data():
    """获取表格数据的API接口"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)
    city_filter = request.args.get('city', '', type=str)
    province_filter = request.args.get('province', '', type=str)
    
    # 确保分页参数的有效性
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    if per_page > 100:  # 限制最大每页显示数量
        per_page = 100
    
    # 构建查询
    query = Attraction.query
    
    # 搜索过滤
    if search and search.strip():
        query = query.filter(Attraction.name.contains(search.strip()))
    
    # 城市过滤
    if city_filter and city_filter.strip():
        query = query.filter(Attraction.city == city_filter.strip())
    
    # 省份过滤
    if province_filter and province_filter.strip():
        query = query.filter(Attraction.province == province_filter.strip())
    
    # 分页
    try:
        pagination = query.order_by(Attraction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    except Exception as e:
        # 如果分页出错，返回第一页
        pagination = query.order_by(Attraction.created_at.desc()).paginate(
            page=1, per_page=per_page, error_out=False
        )
    
    attractions = [attraction.to_dict() for attraction in pagination.items]
    
    # 获取所有城市和省份用于过滤
    cities = db.session.query(Attraction.city).filter(
        Attraction.city.isnot(None), 
        Attraction.city != ''
    ).distinct().all()
    provinces = db.session.query(Attraction.province).filter(
        Attraction.province.isnot(None),
        Attraction.province != ''
    ).distinct().all()
    
    return jsonify({
        'attractions': attractions,
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        },
        'filters': {
            'cities': sorted([city[0] for city in cities if city[0]]),
            'provinces': sorted([province[0] for province in provinces if province[0]])
        },
        'current_filters': {
            'search': search,
            'city': city_filter,
            'province': province_filter,
            'per_page': per_page
        }
    })
