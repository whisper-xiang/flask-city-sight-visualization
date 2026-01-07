import pandas as pd
import numpy as np
import re
from app import db
from app.models import Attraction

class DataProcessor:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        
    def load_and_clean_data(self):
        """加载并清洗CSV数据"""
        try:
            df = pd.read_csv(self.csv_file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(self.csv_file_path, encoding='gbk')
        
        # 数据清洗
        df = self._clean_data(df)
        
        return df
    
    def _clean_data(self, df):
        """数据清洗处理"""
        # 重命名列名（根据实际CSV文件结构调整）
        column_mapping = {
            '名字': 'name',
            '链接': 'link', 
            '地址': 'address',
            '介绍': 'description',
            '开放时间': 'opening_hours',
            '图片链接': 'image_url',
            '评分': 'rating',
            '建议游玩时间': 'recommended_duration',
            '建议季节': 'recommended_season',
            '门票': 'ticket_price',
            '小贴士': 'tips'
        }
        
        # 只重命名存在的列
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)
        
        # 处理缺失值
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['rating'] = df['rating'].fillna(0)
        
        # 提取地理信息
        df = self._extract_location_info(df)
        
        return df
    
    def _extract_location_info(self, df):
        """从地址中提取省市区信息"""
        df['province'] = ''
        df['city'] = ''
        df['district'] = ''
        
        for idx, row in df.iterrows():
            if pd.notna(row['address']):
                location = self._parse_address(row['address'])
                df.at[idx, 'province'] = location.get('province', '')
                df.at[idx, 'city'] = location.get('city', '')
                df.at[idx, 'district'] = location.get('district', '')
        
        return df
    
    def _parse_address(self, address):
        """解析地址信息"""
        province = ''
        city = ''
        district = ''
        
        # 省份匹配
        province_pattern = r'(北京|天津|上海|重庆|河北|山西|辽宁|吉林|黑龙江|江苏|浙江|安徽|福建|江西|山东|河南|湖北|湖南|广东|海南|四川|贵州|云南|陕西|甘肃|青海|台湾|内蒙古|广西|西藏|宁夏|新疆|香港|澳门)(省|市|自治区|特别行政区)?'
        province_match = re.search(province_pattern, address)
        if province_match:
            province = province_match.group(1)
        
        # 城市匹配
        city_pattern = r'([^省]+市|[^自治区]+自治州|[^地区]+地区)'
        city_match = re.search(city_pattern, address)
        if city_match:
            city = city_match.group(1)
        
        # 区县匹配
        district_pattern = r'([^市]+市|[^区]+区|[^县]+县)'
        district_match = re.search(district_pattern, address)
        if district_match:
            district = district_match.group(1)
        
        return {
            'province': province,
            'city': city,
            'district': district
        }
    
    def save_to_database(self, df):
        """将清洗后的数据保存到数据库"""
        # 清空现有数据
        Attraction.query.delete()
        
        # 批量插入数据
        for idx, row in df.iterrows():
            attraction = Attraction(
                name=row.get('name', ''),
                link=row.get('link', ''),
                address=row.get('address', ''),
                description=row.get('description', ''),
                opening_hours=row.get('opening_hours', ''),
                image_url=row.get('image_url', ''),
                rating=float(row.get('rating', 0)) if pd.notna(row.get('rating')) else 0,
                recommended_duration=row.get('recommended_duration', ''),
                recommended_season=row.get('recommended_season', ''),
                ticket_price=row.get('ticket_price', ''),
                tips=row.get('tips', ''),
                province=row.get('province', ''),
                city=row.get('city', ''),
                district=row.get('district', ''),
                latitude=None,  # 后续可以通过地理编码API获取
                longitude=None
            )
            db.session.add(attraction)
        
        db.session.commit()
        print(f"成功导入 {len(df)} 条景点数据")
