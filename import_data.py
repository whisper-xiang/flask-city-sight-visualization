#!/usr/bin/env python3
"""
数据库导入脚本
将清洗后的景点数据导入到MySQL数据库
"""

import os
import sys
import pandas as pd
from pathlib import Path
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import Attraction

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseImporter:
    """数据库导入器"""
    
    def __init__(self, app):
        self.app = app
    
    def import_from_csv(self, csv_file_path: str, batch_size: int = 1000) -> bool:
        """从CSV文件导入数据"""
        try:
            logger.info(f"开始导入数据: {csv_file_path}")
            
            # 读取CSV文件
            try:
                df = pd.read_csv(csv_file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(csv_file_path, encoding='gbk')
            
            logger.info(f"读取到 {len(df)} 条记录")
            
            # 数据预处理
            df = self._preprocess_dataframe(df)
            
            # 批量导入
            with self.app.app_context():
                # 清空现有数据
                logger.info("清空现有数据...")
                Attraction.query.delete()
                db.session.commit()
                
                # 分批导入
                total_imported = 0
                for i in range(0, len(df), batch_size):
                    batch_df = df.iloc[i:i+batch_size]
                    
                    for _, row in batch_df.iterrows():
                        attraction = self._create_attraction_from_row(row)
                        db.session.add(attraction)
                    
                    db.session.commit()
                    total_imported += len(batch_df)
                    logger.info(f"已导入 {total_imported}/{len(df)} 条记录")
                
                logger.info(f"数据导入完成! 总共导入 {total_imported} 条记录")
                return True
                
        except Exception as e:
            logger.error(f"数据导入失败: {e}")
            if 'db.session' in locals():
                db.session.rollback()
            return False
    
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """预处理DataFrame"""
        # 列名映射
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
            '小贴士': 'tips',
            'province': 'province',
            'city': 'city',
            'district': 'district'
        }
        
        # 重命名列
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # 处理缺失值
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        
        # 确保所有必需列存在
        required_columns = ['name', 'rating', 'province', 'city']
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        return df
    
    def _create_attraction_from_row(self, row) -> Attraction:
        """从DataFrame行创建Attraction对象"""
        def clean_value(value):
            """清理值，处理nan和空值"""
            if pd.isna(value) or value == 'nan' or str(value).strip() == 'nan':
                return None
            return str(value) if str(value).strip() != '' else None
        
        return Attraction(
            name=clean_value(row.get('name')) or '未命名景点',
            link=clean_value(row.get('link')),
            address=clean_value(row.get('address')),
            description=clean_value(row.get('description')),
            opening_hours=clean_value(row.get('opening_hours')),
            image_url=clean_value(row.get('image_url')),
            rating=float(row.get('rating', 0)) if pd.notna(row.get('rating')) and str(row.get('rating')).strip() != 'nan' else 0,
            recommended_duration=clean_value(row.get('recommended_duration')),
            recommended_season=clean_value(row.get('recommended_season')),
            ticket_price=clean_value(row.get('ticket_price')) or '暂无信息',
            tips=clean_value(row.get('tips')),
            province=clean_value(row.get('province')) or '未知',
            city=clean_value(row.get('city')) or '未知',
            district=clean_value(row.get('district')),
            latitude=None,  # 后续可以通过地理编码API获取
            longitude=None
        )
    
    def get_import_statistics(self) -> dict:
        """获取导入统计信息"""
        with self.app.app_context():
            total_attractions = Attraction.query.count()
            avg_rating = db.session.query(db.func.avg(Attraction.rating)).scalar() or 0
            
            province_stats = db.session.query(
                Attraction.province,
                db.func.count(Attraction.id)
            ).group_by(Attraction.province).all()
            
            return {
                'total_attractions': total_attractions,
                'average_rating': round(avg_rating, 2),
                'province_distribution': {p: c for p, c in province_stats if p}
            }

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库导入工具')
    parser.add_argument('csv_file', help='CSV文件路径')
    parser.add_argument('--batch-size', type=int, default=1000, help='批处理大小')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    csv_file = Path(args.csv_file)
    if not csv_file.exists():
        logger.error(f"文件不存在: {csv_file}")
        sys.exit(1)
    
    # 创建Flask应用
    app = create_app()
    
    # 创建导入器
    importer = DatabaseImporter(app)
    
    # 执行导入
    success = importer.import_from_csv(str(csv_file), args.batch_size)
    
    if success:
        # 显示统计信息
        stats = importer.get_import_statistics()
        logger.info("导入统计信息:")
        logger.info(f"  总景点数: {stats['total_attractions']}")
        logger.info(f"  平均评分: {stats['average_rating']}")
        logger.info(f"  省份数量: {len(stats['province_distribution'])}")
        
        logger.info("数据库导入成功完成!")
        sys.exit(0)
    else:
        logger.error("数据库导入失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
