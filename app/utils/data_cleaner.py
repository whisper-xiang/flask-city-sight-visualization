import pandas as pd
import numpy as np
import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗工具类"""
    
    def __init__(self):
        self.provinces = self._load_provinces()
        self.cities = self._load_cities()
    
    def _load_provinces(self) -> List[str]:
        """加载省份列表"""
        return [
            '北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
            '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
            '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
            '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门'
        ]
    
    def _load_cities(self) -> Dict[str, List[str]]:
        """加载主要城市列表"""
        return {
            '北京': ['东城', '西城', '朝阳', '丰台', '石景山', '海淀', '门头沟', '房山', '通州', '顺义', '昌平', '大兴', '怀柔', '平谷', '密云', '延庆'],
            '上海': ['黄浦', '徐汇', '长宁', '静安', '普陀', '虹口', '杨浦', '闵行', '宝山', '嘉定', '浦东', '金山', '松江', '青浦', '奉贤', '崇明'],
            '广东': ['广州', '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮'],
            '浙江': ['杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '衢州', '舟山', '台州', '丽水'],
            '江苏': ['南京', '无锡', '徐州', '常州', '苏州', '南通', '连云港', '淮安', '盐城', '扬州', '镇江', '泰州', '宿迁']
        }
    
    def clean_attraction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗景点数据"""
        logger.info("开始数据清洗...")
        
        # 1. 基础字段清洗
        df = self._clean_basic_fields(df)
        
        # 2. 地址信息提取
        df = self._extract_location_info(df)
        
        # 3. 评分标准化
        df = self._normalize_ratings(df)
        
        # 4. 价格信息处理
        df = self._clean_price_info(df)
        
        # 5. 时间信息标准化
        df = self._normalize_time_info(df)
        
        # 6. 季节信息标准化
        df = self._normalize_season_info(df)
        
        # 7. 去重处理
        df = self._remove_duplicates(df)
        
        # 8. 缺失值处理
        df = self._handle_missing_values(df)
        
        logger.info(f"数据清洗完成，剩余 {len(df)} 条记录")
        return df
    
    def _clean_basic_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗基础字段"""
        # 清理名称字段
        if '名字' in df.columns:
            df['名字'] = df['名字'].astype(str).str.strip()
            df['名字'] = df['名字'].str.replace(r'\s+', ' ', regex=True)
        
        # 清理描述字段
        if '介绍' in df.columns:
            df['介绍'] = df['介绍'].astype(str).str.strip()
            df['介绍'] = df['介绍'].str.replace(r'\s+', ' ', regex=True)
            df['介绍'] = df['介绍'].str.replace(r'\n+', ' ', regex=True)
        
        # 清理链接字段
        if '链接' in df.columns:
            df['链接'] = df['链接'].astype(str).str.strip()
            df['链接'] = df['链接'].apply(self._validate_url)
        
        return df
    
    def _extract_location_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取地理位置信息"""
        if '地址' not in df.columns:
            df['地址'] = ''
        
        # 初始化地理位置字段
        df['province'] = ''
        df['city'] = ''
        df['district'] = ''
        
        for idx, row in df.iterrows():
            address = str(row.get('地址', ''))
            if address and address != 'nan':
                location = self._parse_address(address)
                df.at[idx, 'province'] = location['province']
                df.at[idx, 'city'] = location['city']
                df.at[idx, 'district'] = location['district']
        
        return df
    
    def _parse_address(self, address: str) -> Dict[str, str]:
        """解析地址信息"""
        province = ''
        city = ''
        district = ''
        
        # 省份匹配
        for prov in self.provinces:
            if prov in address:
                province = prov
                break
        
        # 城市匹配
        if province in self.cities:
            for city_name in self.cities[province]:
                if city_name in address:
                    city = city_name
                    break
        
        # 区县匹配
        district_patterns = [
            r'([^市]+市)', r'([^区]+区)', r'([^县]+县)', r'([^镇]+镇)'
        ]
        for pattern in district_patterns:
            match = re.search(pattern, address)
            if match and match.group(1) not in [province, city]:
                district = match.group(1)
                break
        
        return {'province': province, 'city': city, 'district': district}
    
    def _normalize_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化评分"""
        if '评分' in df.columns:
            # 转换为数值
            df['评分'] = pd.to_numeric(df['评分'], errors='coerce')
            
            # 处理异常值
            df['评分'] = df['评分'].clip(lower=0, upper=5)
            
            # 填充缺失值
            df['评分'] = df['评分'].fillna(0)
        
        return df
    
    def _clean_price_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗价格信息"""
        if '门票' in df.columns:
            df['门票'] = df['门票'].astype(str).str.strip()
            
            # 标准化免费标识
            df['门票'] = df['门票'].apply(self._normalize_price)
        
        return df
    
    def _normalize_price(self, price_str: str) -> str:
        """标准化价格字符串"""
        if not price_str or price_str == 'nan':
            return '暂无信息'
        
        price_str = price_str.strip()
        
        # 免费关键词
        free_keywords = ['免费', '0元', '无需门票', '不收费']
        for keyword in free_keywords:
            if keyword in price_str:
                return '免费'
        
        # 提取价格数字
        price_match = re.search(r'(\d+\.?\d*)\s*元', price_str)
        if price_match:
            price = float(price_match.group(1))
            if price == 0:
                return '免费'
            elif price < 50:
                return f'{price:.0f}元'
            elif price < 100:
                return f'{price:.0f}元'
            elif price < 200:
                return f'{price:.0f}元'
            else:
                return f'{price:.0f}元以上'
        
        return price_str
    
    def _normalize_time_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化时间信息"""
        if '建议游玩时间' in df.columns:
            df['建议游玩时间'] = df['建议游玩时间'].astype(str).str.strip()
            df['建议游玩时间'] = df['建议游玩时间'].apply(self._normalize_duration)
        
        if '开放时间' in df.columns:
            df['开放时间'] = df['开放时间'].astype(str).str.strip()
        
        return df
    
    def _normalize_duration(self, duration_str: str) -> str:
        """标准化游玩时长"""
        if not duration_str or duration_str == 'nan':
            return '暂无信息'
        
        duration_str = duration_str.strip()
        
        # 提取小时数
        hour_patterns = [
            r'(\d+\.?\d*)\s*小时',
            r'(\d+)\s*小时以上',
            r'(\d+)-(\d+)\s*小时',
            r'(\d+)\s*h'
        ]
        
        for pattern in hour_patterns:
            match = re.search(pattern, duration_str)
            if match:
                if '-' in match.group(0):  # 范围
                    start, end = match.groups()
                    avg_hours = (float(start) + float(end)) / 2
                else:
                    avg_hours = float(match.group(1))
                
                # 标准化输出
                if avg_hours <= 2:
                    return '1-2小时'
                elif avg_hours <= 4:
                    return '2-4小时'
                elif avg_hours <= 8:
                    return '半天'
                else:
                    return '1天以上'
        
        # 处理特殊描述
        if '半天' in duration_str:
            return '半天'
        elif '一天' in duration_str or '1天' in duration_str:
            return '1天'
        elif '两' in duration_str or '2天' in duration_str:
            return '1-2天'
        
        return duration_str
    
    def _normalize_season_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化季节信息"""
        if '建议季节' in df.columns:
            df['建议季节'] = df['建议季节'].astype(str).str.strip()
            df['建议季节'] = df['建议季节'].apply(self._normalize_season)
        
        return df
    
    def _normalize_season(self, season_str: str) -> str:
        """标准化季节"""
        if not season_str or season_str == 'nan':
            return '四季皆宜'
        
        season_str = season_str.strip()
        
        # 季节关键词映射
        season_mapping = {
            '春': '春季', '夏': '夏季', '秋': '秋季', '冬': '冬季',
            '春天': '春季', '夏天': '夏季', '秋天': '秋季', '冬天': '冬季',
            '春季': '春季', '夏季': '夏季', '秋季': '秋季', '冬季': '冬季',
            '四季': '四季皆宜', '全年': '四季皆宜', '任何季节': '四季皆宜'
        }
        
        for key, value in season_mapping.items():
            if key in season_str:
                return value
        
        # 检查是否包含多个季节
        seasons = []
        if '春' in season_str or '春季' in season_str:
            seasons.append('春季')
        if '夏' in season_str or '夏季' in season_str:
            seasons.append('夏季')
        if '秋' in season_str or '秋季' in season_str:
            seasons.append('秋季')
        if '冬' in season_str or '冬季' in season_str:
            seasons.append('冬季')
        
        if len(seasons) >= 3:
            return '四季皆宜'
        elif len(seasons) > 1:
            return '、'.join(seasons)
        elif len(seasons) == 1:
            return seasons[0]
        
        return season_str
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """去重处理"""
        # 基于名称和地址去重
        if '名字' in df.columns and '地址' in df.columns:
            df['name_addr_key'] = df['名字'].astype(str) + '_' + df['地址'].astype(str)
            df = df.drop_duplicates(subset=['name_addr_key'], keep='first')
            df = df.drop('name_addr_key', axis=1)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        # 数值字段填充
        numeric_columns = ['评分']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # 文本字段填充
        text_columns = ['名字', '地址', '介绍', '门票', '建议游玩时间', '建议季节']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('暂无信息')
                df[col] = df[col].replace('', '暂无信息')
                df[col] = df[col].replace('nan', '暂无信息')
        
        return df
    
    def _validate_url(self, url: str) -> str:
        """验证URL格式"""
        if not url or url == 'nan':
            return ''
        
        url = url.strip()
        if url and not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        return url
    
    def generate_data_report(self, df: pd.DataFrame) -> Dict:
        """生成数据报告"""
        report = {
            '总记录数': len(df),
            '字段统计': {},
            '数据质量': {}
        }
        
        # 字段统计
        for col in df.columns:
            report['字段统计'][col] = {
                '非空数量': df[col].notna().sum(),
                '唯一值数量': df[col].nunique(),
                '数据类型': str(df[col].dtype)
            }
        
        # 数据质量
        if '评分' in df.columns:
            report['数据质量']['评分分布'] = df['评分'].describe().to_dict()
        
        if 'province' in df.columns:
            report['数据质量']['省份分布'] = df['province'].value_counts().head(10).to_dict()
        
        return report

def main():
    """主函数 - 演示数据清洗"""
    print("开始数据清洗...")
    
    # 创建数据清洗器
    cleaner = DataCleaner()
    
    # 读取原始数据
    data_file = Path("data/china_city_attraction_details.csv")
    if data_file.exists():
        try:
            df = pd.read_csv(data_file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(data_file, encoding='gbk')
        
        print(f"读取原始数据: {len(df)} 条记录")
        
        # 数据清洗
        cleaned_df = cleaner.clean_attraction_data(df)
        
        # 保存清洗后的数据
        output_file = Path("data/cleaned_attractions.csv")
        cleaned_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"清洗后数据: {len(cleaned_df)} 条记录")
        print(f"清洗后数据已保存到: {output_file}")
        
        # 生成数据报告
        report = cleaner.generate_data_report(cleaned_df)
        report_file = Path("data/data_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"数据报告已保存到: {report_file}")
        
    else:
        print("未找到原始数据文件")
    
    print("数据清洗完成")

if __name__ == "__main__":
    main()
