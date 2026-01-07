from flask import Blueprint, render_template, jsonify
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
