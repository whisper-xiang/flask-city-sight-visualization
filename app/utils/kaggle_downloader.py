import requests
import os
import zipfile
import pandas as pd
from pathlib import Path
import time
from typing import Optional

class KaggleDataDownloader:
    """Kaggle数据集下载器"""
    
    def __init__(self, dataset_name: str, data_dir: str = "data"):
        self.dataset_name = dataset_name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def download_from_kaggle(self, kaggle_json_path: Optional[str] = None) -> bool:
        """
        从Kaggle下载数据集
        需要先配置Kaggle API认证
        """
        try:
            # 尝试使用kaggle库下载
            return self._download_with_kaggle_api(kaggle_json_path)
        except ImportError:
            print("Kaggle库未安装，尝试直接下载...")
            return self._download_directly()
        except Exception as e:
            print(f"Kaggle下载失败: {e}")
            return False
    
    def _download_with_kaggle_api(self, kaggle_json_path: Optional[str] = None) -> bool:
        """使用Kaggle API下载"""
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            # 设置API认证
            if kaggle_json_path and os.path.exists(kaggle_json_path):
                os.environ['KAGGLE_CONFIG_DIR'] = os.path.dirname(kaggle_json_path)
            
            api = KaggleApi()
            api.authenticate()
            
            # 下载数据集
            print(f"正在下载数据集: {self.dataset_name}")
            api.dataset_download_files(
                self.dataset_name, 
                path=str(self.data_dir),
                unzip=True
            )
            
            print("数据集下载完成")
            return True
            
        except Exception as e:
            print(f"Kaggle API下载失败: {e}")
            return False
    
    def _download_directly(self) -> bool:
        """直接从URL下载（如果可用）"""
        # 这里可以实现直接下载逻辑
        # 由于Kaggle需要认证，主要还是推荐使用API
        print("直接下载需要手动配置，建议使用Kaggle API")
        return False
    
    def download_sample_data(self) -> bool:
        """下载示例数据或创建模拟数据"""
        try:
            # 创建示例数据
            sample_data = self._create_sample_data()
            
            # 保存为CSV
            csv_path = self.data_dir / "china_city_attraction_details.csv"
            sample_data.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            print(f"示例数据已创建: {csv_path}")
            print(f"数据量: {len(sample_data)} 条记录")
            return True
            
        except Exception as e:
            print(f"创建示例数据失败: {e}")
            return False
    
    def _create_sample_data(self) -> pd.DataFrame:
        """创建示例景点数据"""
        import random
        
        # 示例数据
        provinces = ['北京', '上海', '广东', '浙江', '江苏', '四川', '云南', '陕西']
        cities = {
            '北京': ['北京'],
            '上海': ['上海'],
            '广东': ['广州', '深圳', '珠海', '佛山'],
            '浙江': ['杭州', '宁波', '温州', '绍兴'],
            '江苏': ['南京', '苏州', '无锡', '常州'],
            '四川': ['成都', '绵阳', '乐山', '九寨沟'],
            '云南': ['昆明', '大理', '丽江', '香格里拉'],
            '陕西': ['西安', '延安', '华山', '宝鸡']
        }
        
        attractions = []
        attraction_names = [
            '故宫博物院', '长城', '天坛公园', '颐和园', '鸟巢', '水立方',
            '外滩', '东方明珠', '豫园', '城隍庙', '南京路', '田子坊',
            '西湖', '灵隐寺', '雷峰塔', '千岛湖', '普陀山', '雁荡山',
            '中山陵', '夫子庙', '玄武湖', '明孝陵', '总统府', '秦淮河',
            '宽窄巷子', '锦里', '武侯祠', '杜甫草堂', '青城山', '都江堰',
            '石林', '滇池', '西山', '翠湖', '金马碧鸡坊', '云南民族村',
            '兵马俑', '大雁塔', '华清池', '钟鼓楼', '回民街', '古城墙'
        ]
        
        seasons = ['春季', '夏季', '秋季', '冬季', '四季皆宜']
        durations = ['1-2小时', '2-3小时', '3-4小时', '半天', '一天', '1-2天']
        ticket_prices = ['免费', '30元', '50元', '80元', '100元', '150元', '200元']
        
        for i in range(100):  # 创建100条示例数据
            province = random.choice(provinces)
            city = random.choice(cities[province])
            
            attraction = {
                '名字': random.choice(attraction_names) + f'_{i}',
                '链接': f'https://example.com/attraction_{i}',
                '地址': f'{province}{city}某区某街道{i}号',
                '介绍': f'这是一个位于{province}{city}的著名景点，有着丰富的历史文化底蕴...',
                '开放时间': f'{random.randint(8, 9)}:00-{random.randint(17, 18)}:00',
                '图片链接': f'https://example.com/images/attraction_{i}.jpg',
                '评分': round(random.uniform(3.5, 5.0), 1),
                '建议游玩时间': random.choice(durations),
                '建议季节': random.choice(seasons),
                '门票': random.choice(ticket_prices),
                '小贴士': f'建议{random.choice(["早上", "下午", "晚上"])}前往，{random.choice(["避开人流", "注意防晒", "带好相机"])}'
            }
            attractions.append(attraction)
        
        return pd.DataFrame(attractions)

def main():
    """主函数"""
    # 创建下载器
    downloader = KaggleDataDownloader("audreyhengruizhang/china-city-attraction-details")
    
    # 尝试从Kaggle下载
    print("尝试从Kaggle下载数据集...")
    success = downloader.download_from_kaggle()
    
    if not success:
        print("Kaggle下载失败，创建示例数据...")
        success = downloader.download_sample_data()
    
    if success:
        print("数据获取成功！")
    else:
        print("数据获取失败！")

if __name__ == "__main__":
    main()
