import pandas as pd
import numpy as np
from app.models import Attraction
from app import db
import jieba
from collections import Counter
import re

class DataAnalyzer:
    def __init__(self):
        pass
    
    def get_all_statistics(self):
        """获取所有基础统计数据"""
        total_attractions = Attraction.query.count()
        avg_rating = db.session.query(db.func.avg(Attraction.rating)).scalar() or 0
        free_count = Attraction.query.filter(Attraction.ticket_price == '免费').count()
        paid_count = total_attractions - free_count
        
        return {
            'total_attractions': total_attractions,
            'avg_rating': round(avg_rating, 2),
            'free_attractions': free_count,
            'paid_attractions': paid_count
        }
    
    def get_rating_distribution(self):
        """获取评分分布数据"""
        ratings = db.session.query(Attraction.rating).all()
        rating_list = [r[0] for r in ratings if r[0]]
        
        # 创建评分区间
        bins = [0, 2, 3, 4, 4.5, 5]
        labels = ['0-2', '2-3', '3-4', '4-4.5', '4.5-5']
        
        distribution = pd.cut(rating_list, bins=bins, labels=labels, right=True)
        counts = distribution.value_counts().sort_index()
        
        return {
            'labels': labels,
            'data': counts.tolist()
        }
    
    def get_season_distribution(self):
        """获取季节推荐分布"""
        seasons = db.session.query(Attraction.recommended_season).all()
        season_list = [s[0] for s in seasons if s[0]]
        
        season_counts = Counter(season_list)
        
        return {
            'labels': list(season_counts.keys()),
            'data': list(season_counts.values())
        }
    
    def get_rating_duration_correlation(self):
        """获取评分与建议访问时长的相关性"""
        attractions = db.session.query(Attraction.rating, Attraction.recommended_duration).all()
        
        # 清理和标准化时长数据
        duration_data = []
        for rating, duration in attractions:
            if rating and duration:
                # 提取数字（小时）
                hours = self._extract_hours(duration)
                if hours:
                    duration_data.append({'rating': rating, 'duration': hours})
        
        return duration_data
    
    def get_province_distribution(self):
        """获取省份分布数据"""
        provinces = db.session.query(Attraction.province).all()
        province_list = [p[0] for p in provinces if p[0]]
        
        province_counts = Counter(province_list)
        
        # 取前15个省份
        top_provinces = province_counts.most_common(15)
        
        return {
            'labels': [p[0] for p in top_provinces],
            'data': [p[1] for p in top_provinces]
        }
    
    def get_geo_distribution(self):
        """获取地理分布数据（用于地图展示）"""
        attractions = db.session.query(
            Attraction.name, 
            Attraction.rating,
            Attraction.province,
            Attraction.city,
            Attraction.latitude,
            Attraction.longitude
        ).filter(Attraction.latitude.isnot(None), Attraction.longitude.isnot(None)).all()
        
        geo_data = []
        for attraction in attractions:
            geo_data.append({
                'name': attraction[0],
                'value': [attraction[4], attraction[5], attraction[1] or 0],  # [lat, lng, rating]
                'province': attraction[2],
                'city': attraction[3]
            })
        
        return geo_data
    
    def _extract_hours(self, duration_str):
        """从建议访问时长中提取小时数"""
        if not duration_str:
            return None
            
        # 匹配数字和单位
        patterns = [
            r'(\d+\.?\d*)\s*小时',
            r'(\d+\.?\d*)\s*h',
            r'(\d+)\s*小时以上',
            r'(\d+)-(\d+)\s*小时'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, duration_str)
            if match:
                if '-' in match.group(0):  # 范围
                    start, end = match.groups()
                    return (float(start) + float(end)) / 2
                else:
                    return float(match.group(1))
        
        return None
