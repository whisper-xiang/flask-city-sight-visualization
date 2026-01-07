#!/usr/bin/env python3
"""
数据采集主脚本
整合Kaggle下载、网页爬取和数据清洗功能
"""

import os
import sys
import argparse
from pathlib import Path
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.kaggle_downloader import KaggleDataDownloader
from app.utils.web_scraper import CtripAttractionScraper, DianpingAttractionScraper
from app.utils.data_cleaner import DataCleaner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollectionManager:
    """数据采集管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def run_full_pipeline(self, use_kaggle: bool = True, use_web_scraping: bool = False):
        """运行完整数据采集流程"""
        logger.info("开始数据采集流程...")
        
        # 1. 从Kaggle获取数据
        if use_kaggle:
            logger.info("步骤1: 从Kaggle获取数据")
            kaggle_success = self._download_from_kaggle()
        else:
            kaggle_success = False
        
        # 2. 网页爬取（可选）
        if use_web_scraping:
            logger.info("步骤2: 网页爬取补充数据")
            scraping_success = self._run_web_scraping()
        else:
            scraping_success = False
        
        # 3. 数据清洗
        logger.info("步骤3: 数据清洗处理")
        cleaning_success = self._clean_data()
        
        # 4. 生成报告
        logger.info("步骤4: 生成数据报告")
        self._generate_collection_report()
        
        logger.info("数据采集流程完成!")
        
        return kaggle_success or scraping_success and cleaning_success
    
    def _download_from_kaggle(self) -> bool:
        """从Kaggle下载数据"""
        try:
            downloader = KaggleDataDownloader(
                "audreyhengruizhang/china-city-attraction-details",
                str(self.data_dir)
            )
            
            # 尝试从Kaggle下载
            success = downloader.download_from_kaggle()
            
            if not success:
                logger.warning("Kaggle下载失败，创建示例数据")
                success = downloader.download_sample_data()
            
            return success
            
        except Exception as e:
            logger.error(f"Kaggle下载失败: {e}")
            return False
    
    def _run_web_scraping(self) -> bool:
        """运行网页爬取"""
        try:
            all_attractions = []
            
            # 携程爬取
            logger.info("爬取携程景点数据...")
            ctrip_scraper = CtripAttractionScraper()
            
            cities = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'hangzhou']
            for city in cities:
                logger.info(f"爬取{city}景点...")
                attractions = ctrip_scraper.search_attractions(city, page=1)
                all_attractions.extend(attractions)
                
                # 保存单个城市数据
                ctrip_scraper.save_data(attractions, f"{city}_attractions_ctrip.csv")
            
            # 大众点评爬取
            logger.info("爬取大众点评景点数据...")
            dianping_scraper = DianpingAttractionScraper()
            
            for city in ['北京', '上海', '广州', '深圳', '杭州']:
                logger.info(f"爬取{city}景点...")
                attractions = dianping_scraper.search_attractions(city)
                all_attractions.extend(attractions)
                
                # 保存单个城市数据
                dianping_scraper.save_data(attractions, f"{city}_attractions_dianping.csv")
            
            # 合并所有爬取数据
            if all_attractions:
                import pandas as pd
                df = pd.DataFrame(all_attractions)
                output_file = self.data_dir / "scraped_attractions.csv"
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                logger.info(f"爬取数据已保存到: {output_file}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"网页爬取失败: {e}")
            return False
    
    def _clean_data(self) -> bool:
        """数据清洗"""
        try:
            cleaner = DataCleaner()
            
            # 查找需要清洗的数据文件
            data_files = list(self.data_dir.glob("*attractions*.csv"))
            
            if not data_files:
                logger.warning("未找到需要清洗的数据文件")
                return False
            
            all_cleaned_data = []
            
            for data_file in data_files:
                if 'cleaned' in data_file.name:
                    continue  # 跳过已清洗的文件
                
                logger.info(f"清洗数据文件: {data_file}")
                
                try:
                    # 读取数据
                    df = pd.read_csv(data_file, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(data_file, encoding='gbk')
                
                # 数据清洗
                cleaned_df = cleaner.clean_attraction_data(df)
                all_cleaned_data.append(cleaned_df)
                
                # 保存清洗后的数据
                cleaned_filename = f"cleaned_{data_file.name}"
                cleaned_file = self.data_dir / cleaned_filename
                cleaned_df.to_csv(cleaned_file, index=False, encoding='utf-8-sig')
                logger.info(f"清洗后数据已保存到: {cleaned_file}")
                
            # 合并所有清洗后的数据
            if all_cleaned_data:
                import pandas as pd
                combined_df = pd.concat(all_cleaned_data, ignore_index=True)
                
                # 去重
                combined_df = combined_df.drop_duplicates(subset=['名字', '地址'], keep='first')
                
                # 保存最终数据
                final_file = self.data_dir / "final_attractions.csv"
                combined_df.to_csv(final_file, index=False, encoding='utf-8-sig')
                logger.info(f"最终合并数据已保存到: {final_file}")
                logger.info(f"最终数据量: {len(combined_df)} 条记录")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"数据清洗失败: {e}")
            return False
    
    def _generate_collection_report(self):
        """生成数据采集报告"""
        try:
            import json
            import pandas as pd
            from datetime import datetime
            
            report = {
                '采集时间': datetime.now().isoformat(),
                '数据文件': [],
                '统计信息': {}
            }
            
            # 扫描数据文件
            for file_path in self.data_dir.glob("*.csv"):
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')
                    file_info = {
                        '文件名': file_path.name,
                        '记录数': len(df),
                        '字段数': len(df.columns),
                        '文件大小': f"{file_path.stat().st_size / 1024:.1f} KB"
                    }
                    report['数据文件'].append(file_info)
                except Exception as e:
                    logger.warning(f"无法读取文件 {file_path}: {e}")
            
            # 保存报告
            report_file = self.data_dir / "collection_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据采集报告已保存到: {report_file}")
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='城市景点数据采集工具')
    parser.add_argument('--data-dir', default='data', help='数据目录')
    parser.add_argument('--kaggle', action='store_true', help='使用Kaggle数据')
    parser.add_argument('--scraping', action='store_true', help='使用网页爬取')
    parser.add_argument('--all', action='store_true', help='运行完整流程')
    
    args = parser.parse_args()
    
    # 创建数据采集管理器
    manager = DataCollectionManager(args.data_dir)
    
    if args.all:
        # 运行完整流程
        success = manager.run_full_pipeline(
            use_kaggle=True,
            use_web_scraping=args.scraping
        )
    elif args.kaggle:
        # 仅Kaggle下载
        success = manager._download_from_kaggle()
    elif args.scraping:
        # 仅网页爬取
        success = manager._run_web_scraping()
    else:
        # 默认运行完整流程
        success = manager.run_full_pipeline()
    
    if success:
        logger.info("数据采集任务成功完成!")
        sys.exit(0)
    else:
        logger.error("数据采集任务失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
