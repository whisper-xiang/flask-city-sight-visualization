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
        
        # 新增统计
        high_rated_count = Attraction.query.filter(Attraction.rating >= 4.0).count()
        province_count = db.session.query(db.func.count(db.distinct(Attraction.province))).scalar() or 0
        city_count = db.session.query(db.func.count(db.distinct(Attraction.city))).scalar() or 0
        season_all_count = Attraction.query.filter(Attraction.recommended_season == '四季皆宜').count()
        
        # 计算平均游玩时长
        avg_duration = self._calculate_avg_duration()
        
        return {
            'total_attractions': total_attractions,
            'avg_rating': round(avg_rating, 2),
            'free_attractions': free_count,
            'paid_attractions': paid_count,
            'high_rated_attractions': high_rated_count,
            'province_count': province_count,
            'city_count': city_count,
            'season_all': season_all_count,
            'avg_duration': avg_duration
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
    
    def _calculate_avg_duration(self):
        """计算平均游玩时长"""
        durations = []
        attractions = db.session.query(Attraction.recommended_duration).all()
        
        for duration in attractions:
            if duration[0]:
                hours = self._extract_hours(duration[0])
                if hours:
                    durations.append(hours)
        
        if durations:
            avg_hours = sum(durations) / len(durations)
            if avg_hours < 1:
                return f"{int(avg_hours * 60)}分钟"
            else:
                return f"{avg_hours:.1f}小时"
        return "暂无"
    
    def get_price_distribution(self):
        """获取门票价格分布"""
        prices = db.session.query(Attraction.ticket_price).all()
        price_list = [p[0] for p in prices if p[0]]
        
        price_counts = Counter(price_list)
        
        # 合并相似价格类别
        categorized = {
            '免费': price_counts.get('免费', 0),
            '1-50元': 0,
            '51-100元': 0,
            '101-200元': 0,
            '200元以上': 0,
            '其他': 0
        }
        
        for price, count in price_counts.items():
            if price == '免费':
                continue
            try:
                # 提取数字
                num_match = re.search(r'(\d+)', price)
                if num_match:
                    num = int(num_match.group(1))
                    if num <= 50:
                        categorized['1-50元'] += count
                    elif num <= 100:
                        categorized['51-100元'] += count
                    elif num <= 200:
                        categorized['101-200元'] += count
                    else:
                        categorized['200元以上'] += count
                else:
                    categorized['其他'] += count
            except:
                categorized['其他'] += count
        
        return {
            'data': [{'name': k, 'value': v} for k, v in categorized.items() if v > 0]
        }
    
    def get_duration_distribution(self):
        """获取游玩时长分布"""
        durations = []
        attractions = db.session.query(Attraction.recommended_duration).all()
        
        for duration in attractions:
            if duration[0]:
                hours = self._extract_hours(duration[0])
                if hours:
                    durations.append(hours)
        
        # 创建时长区间 - 修复bins和labels的对应关系
        bins = [0, 1, 2, 3, 5, 10, float('inf')]
        labels = ['<1小时', '1-2小时', '2-3小时', '3-5小时', '5-10小时', '>10小时']
        
        if durations:
            try:
                distribution = pd.cut(durations, bins=bins, labels=labels, right=False, include_lowest=True)
                counts = distribution.value_counts().sort_index()
                
                # 确保所有区间都有数据（即使是0）
                result_data = []
                for label in labels:
                    result_data.append(int(counts.get(label, 0)))
                
                return {
                    'labels': labels,
                    'data': result_data
                }
            except Exception as e:
                print(f"Error in duration distribution: {e}")
                # 如果pandas失败，使用手动计算
                return self._manual_duration_calculation(durations, labels)
        
        return {
            'labels': labels,
            'data': [0] * len(labels)
        }
    
    def _manual_duration_calculation(self, durations, labels):
        """手动计算时长分布（备用方案）"""
        counts = [0] * len(labels)
        
        for hours in durations:
            if hours < 1:
                counts[0] += 1  # <1小时
            elif hours < 2:
                counts[1] += 1  # 1-2小时
            elif hours < 3:
                counts[2] += 1  # 2-3小时
            elif hours < 5:
                counts[3] += 1  # 3-5小时
            elif hours < 10:
                counts[4] += 1  # 5-10小时
            else:
                counts[5] += 1  # >10小时
        
        return {
            'labels': labels,
            'data': counts
        }
    
    def get_top_attractions(self):
        """获取热门景点排行"""
        attractions = db.session.query(
            Attraction.name, 
            Attraction.rating,
            Attraction.province,
            Attraction.city
        ).filter(Attraction.rating >= 4.0).order_by(Attraction.rating.desc()).limit(20).all()
        
        return {
            'labels': [f"{attr[0][:15]}..." if len(attr[0]) > 15 else attr[0] for attr in attractions],
            'data': [float(attr[1]) if attr[1] else 0 for attr in attractions]
        }
