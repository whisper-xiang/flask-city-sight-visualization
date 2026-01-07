from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Attraction, Favorite, Review
from app.utils.data_analyzer import DataAnalyzer

city_bp = Blueprint('city', __name__)

@city_bp.route('/')
def city_index():
    return render_template('city/index.html')

@city_bp.route('/attractions')
def attractions():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # 筛选参数
        province = request.args.get('province')
        city = request.args.get('city')
        rating_min = request.args.get('rating_min', type=float)
        season = request.args.get('season')
        is_free = request.args.get('is_free')
        search = request.args.get('search')
        duration = request.args.get('duration')
        
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
        if search:
            query = query.filter(Attraction.name.contains(search))
        if duration:
            query = query.filter(Attraction.recommended_duration == duration)
        
        attractions = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 如果是AJAX请求，返回JSON
        if request.args.get('format') == 'json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'attractions': [attraction.to_dict() for attraction in attractions.items],
                'pagination': {
                    'page': attractions.page,
                    'pages': attractions.pages,
                    'per_page': attractions.per_page,
                    'total': attractions.total,
                    'has_prev': attractions.has_prev,
                    'has_next': attractions.has_next,
                    'prev_num': attractions.prev_num,
                    'next_num': attractions.next_num
                }
            })
        
        return render_template('city/attractions.html', attractions=attractions)
    
    except Exception as e:
        # 如果是AJAX请求，返回JSON错误
        if request.args.get('format') == 'json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': str(e)}), 500
        # 否则渲染错误页面
        return render_template('errors/500.html', error=str(e)), 500

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

@city_bp.route('/api/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    try:
        attraction_id = request.json.get('attraction_id')
        if not attraction_id:
            return jsonify({'error': '景点ID不能为空'}), 400
        
        # 检查是否已经收藏
        existing = Favorite.query.filter_by(
            user_id=current_user.id, 
            attraction_id=attraction_id
        ).first()
        
        if existing:
            return jsonify({'error': '您已经收藏过这个景点'}), 400
        
        # 检查景点是否存在
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify({'error': '景点不存在'}), 404
        
        # 添加收藏
        favorite = Favorite(user_id=current_user.id, attraction_id=attraction_id)
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({'message': '收藏成功', 'favorite': favorite.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@city_bp.route('/api/favorites/remove', methods=['POST'])
@login_required
def remove_favorite():
    try:
        attraction_id = request.json.get('attraction_id')
        if not attraction_id:
            return jsonify({'error': '景点ID不能为空'}), 400
        
        favorite = Favorite.query.filter_by(
            user_id=current_user.id, 
            attraction_id=attraction_id
        ).first()
        
        if not favorite:
            return jsonify({'error': '您还没有收藏这个景点'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': '取消收藏成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@city_bp.route('/api/favorites/check/<int:attraction_id>')
@login_required
def check_favorite(attraction_id):
    try:
        favorite = Favorite.query.filter_by(
            user_id=current_user.id, 
            attraction_id=attraction_id
        ).first()
        
        return jsonify({
            'is_favorite': favorite is not None,
            'favorite': favorite.to_dict() if favorite else None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 评价相关API
@city_bp.route('/api/reviews/<int:attraction_id>')
def get_reviews(attraction_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        reviews = Review.query.filter_by(attraction_id=attraction_id)\
            .order_by(Review.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # 计算评分统计
        rating_stats = db.session.query(
            db.func.count(Review.id).label('total'),
            db.func.avg(Review.rating).label('avg_rating')
        ).filter_by(attraction_id=attraction_id).first()
        
        return jsonify({
            'reviews': [review.to_dict() for review in reviews.items],
            'pagination': {
                'page': reviews.page,
                'pages': reviews.pages,
                'per_page': reviews.per_page,
                'total': reviews.total,
                'has_prev': reviews.has_prev,
                'has_next': reviews.has_next
            },
            'stats': {
                'total_reviews': rating_stats.total or 0,
                'avg_rating': float(rating_stats.avg_rating) if rating_stats.avg_rating else 0
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@city_bp.route('/api/reviews/add', methods=['POST'])
@login_required
def add_review():
    try:
        attraction_id = request.json.get('attraction_id')
        rating = request.json.get('rating')
        content = request.json.get('content', '')
        
        if not attraction_id or not rating:
            return jsonify({'error': '景点ID和评分不能为空'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'error': '评分必须在1-5之间'}), 400
        
        # 检查是否已经评价过
        existing = Review.query.filter_by(
            user_id=current_user.id, 
            attraction_id=attraction_id
        ).first()
        
        if existing:
            return jsonify({'error': '您已经评价过这个景点'}), 400
        
        # 检查景点是否存在
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return jsonify({'error': '景点不存在'}), 404
        
        # 添加评价
        review = Review(
            user_id=current_user.id,
            attraction_id=attraction_id,
            rating=rating,
            content=content
        )
        db.session.add(review)
        db.session.commit()
        
        return jsonify({'message': '评价成功', 'review': review.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@city_bp.route('/api/reviews/update/<int:review_id>', methods=['PUT'])
@login_required
def update_review(review_id):
    try:
        review = Review.query.get_or_404(review_id)
        
        # 检查是否是当前用户的评价
        if review.user_id != current_user.id:
            return jsonify({'error': '无权修改此评价'}), 403
        
        rating = request.json.get('rating')
        content = request.json.get('content', '')
        
        if rating and not (1 <= rating <= 5):
            return jsonify({'error': '评分必须在1-5之间'}), 400
        
        if rating:
            review.rating = rating
        if content is not None:
            review.content = content
        
        review.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': '评价更新成功', 'review': review.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@city_bp.route('/api/reviews/delete/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    try:
        review = Review.query.get_or_404(review_id)
        
        # 检查是否是当前用户的评价
        if review.user_id != current_user.id:
            return jsonify({'error': '无权删除此评价'}), 403
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({'message': '评价删除成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@city_bp.route('/api/reviews/user/<int:attraction_id>')
@login_required
def get_user_review(attraction_id):
    try:
        review = Review.query.filter_by(
            user_id=current_user.id,
            attraction_id=attraction_id
        ).first()
        
        return jsonify({
            'has_reviewed': review is not None,
            'review': review.to_dict() if review else None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
