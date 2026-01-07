import requests
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import pandas as pd
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path

class WebScraper:
    """通用网页爬虫类"""
    
    def __init__(self, delay_range: tuple = (1, 3)):
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """获取网页内容"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                # 随机延迟
                time.sleep(random.uniform(*self.delay_range))
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except Exception as e:
                print(f"请求失败 (尝试 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    def save_data(self, data: List[Dict], filename: str, format: str = 'csv'):
        """保存数据到文件"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        filepath = data_dir / filename
        
        if format == 'csv':
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        elif format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filepath}")

class CtripAttractionScraper(WebScraper):
    """携程景点爬虫"""
    
    def __init__(self):
        super().__init__(delay_range=(2, 5))
        self.base_url = "https://you.ctrip.com"
    
    def search_attractions(self, city: str, page: int = 1) -> List[Dict]:
        """搜索指定城市的景点"""
        search_url = f"{self.base_url}/sight/{city}/s0-p{page}.html"
        
        soup = self.get_page(search_url)
        if not soup:
            return []
        
        attractions = []
        
        # 解析景点列表（根据实际HTML结构调整选择器）
        attraction_items = soup.find_all('div', class_='list-item')
        
        for item in attraction_items:
            try:
                attraction = self._parse_attraction_item(item)
                if attraction:
                    attractions.append(attraction)
            except Exception as e:
                print(f"解析景点失败: {e}")
                continue
        
        return attractions
    
    def _parse_attraction_item(self, item) -> Optional[Dict]:
        """解析单个景点信息"""
        try:
            # 景点名称
            name_elem = item.find('a', class_='title')
            name = name_elem.text.strip() if name_elem else ""
            
            # 景点链接
            link = name_elem.get('href', '') if name_elem else ""
            if link:
                link = urljoin(self.base_url, link)
            
            # 评分
            rating_elem = item.find('span', class_='score')
            rating = float(rating_elem.text.strip()) if rating_elem else 0.0
            
            # 价格
            price_elem = item.find('span', class_='price')
            price = price_elem.text.strip() if price_elem else ""
            
            # 地址
            address_elem = item.find('div', class_='address')
            address = address_elem.text.strip() if address_elem else ""
            
            # 简介
            desc_elem = item.find('div', class_='desc')
            description = desc_elem.text.strip() if desc_elem else ""
            
            return {
                '名字': name,
                '链接': link,
                '评分': rating,
                '门票': price,
                '地址': address,
                '介绍': description,
                '数据源': '携程'
            }
            
        except Exception as e:
            print(f"解析景点项失败: {e}")
            return None

class DianpingAttractionScraper(WebScraper):
    """大众点评景点爬虫"""
    
    def __init__(self):
        super().__init__(delay_range=(1, 3))
        self.base_url = "https://www.dianping.com"
    
    def search_attractions(self, city: str, category: str = "景点") -> List[Dict]:
        """搜索指定城市的景点"""
        search_url = f"{self.base_url}/{city}/ch{category}"
        
        soup = self.get_page(search_url)
        if not soup:
            return []
        
        attractions = []
        
        # 解析景点列表
        shop_items = soup.find_all('div', class_='shop-list')
        
        for item in shop_items:
            try:
                attraction = self._parse_shop_item(item)
                if attraction:
                    attractions.append(attraction)
            except Exception as e:
                print(f"解析景点失败: {e}")
                continue
        
        return attractions
    
    def _parse_shop_item(self, item) -> Optional[Dict]:
        """解析大众点评店铺信息"""
        try:
            # 店铺名称
            name_elem = item.find('h4')
            name = name_elem.text.strip() if name_elem else ""
            
            # 评分
            rating_elem = item.find('span', class_='comment-star')
            rating = float(rating_elem.get('title', 0)) if rating_elem else 0.0
            
            # 地址
            address_elem = item.find('span', class_='addr')
            address = address_elem.text.strip() if address_elem else ""
            
            # 人均消费
            price_elem = item.find('span', class_='price')
            price = price_elem.text.strip() if price_elem else ""
            
            return {
                '名字': name,
                '评分': rating,
                '门票': price,
                '地址': address,
                '数据源': '大众点评'
            }
            
        except Exception as e:
            print(f"解析店铺项失败: {e}")
            return None

class BaiduAttractionScraper(WebScraper):
    """百度地图景点爬虫"""
    
    def __init__(self):
        super().__init__(delay_range=(1, 2))
        self.search_api = "https://map.baidu.com/su"
    
    def search_attractions(self, city: str, keyword: str = "景点") -> List[Dict]:
        """搜索指定城市的景点"""
        params = {
            'wd': f'{city} {keyword}',
            'type': 2,
            'qt': 'poi',
            'wd2': '',
            'pn': 0,
            'rn': 20
        }
        
        try:
            response = self.session.get(self.search_api, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_baidu_results(data)
            
        except Exception as e:
            print(f"百度搜索失败: {e}")
            return []
    
    def _parse_baidu_results(self, data: Dict) -> List[Dict]:
        """解析百度搜索结果"""
        attractions = []
        
        if 's' in data:
            for item in data['s']:
                try:
                    attraction = {
                        '名字': item.get('name', ''),
                        '地址': item.get('addr', ''),
                        '电话': item.get('tel', ''),
                        '经度': item.get('lng', ''),
                        '纬度': item.get('lat', ''),
                        '数据源': '百度地图'
                    }
                    attractions.append(attraction)
                except Exception as e:
                    print(f"解析百度结果失败: {e}")
                    continue
        
        return attractions

def main():
    """主函数 - 演示爬虫使用"""
    print("开始爬取景点数据...")
    
    # 创建携程爬虫
    ctrip_scraper = CtripAttractionScraper()
    
    # 爬取北京景点（示例）
    print("爬取北京景点...")
    beijing_attractions = ctrip_scraper.search_attractions("beijing", page=1)
    
    if beijing_attractions:
        ctrip_scraper.save_data(beijing_attractions, "beijing_attractions_ctrip.csv")
        print(f"成功爬取 {len(beijing_attractions)} 个北京景点")
    
    # 创建大众点评爬虫
    dianping_scraper = DianpingAttractionScraper()
    
    # 爬取上海景点（示例）
    print("爬取上海景点...")
    shanghai_attractions = dianping_scraper.search_attractions("shanghai")
    
    if shanghai_attractions:
        dianping_scraper.save_data(shanghai_attractions, "shanghai_attractions_dianping.csv")
        print(f"成功爬取 {len(shanghai_attractions)} 个上海景点")
    
    print("爬虫任务完成")

if __name__ == "__main__":
    main()
