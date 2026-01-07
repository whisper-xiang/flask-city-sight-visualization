import pandas as pd
import os
from pathlib import Path

def merge_city_data():
    """合并所有城市数据"""
    data_dir = Path("data/citydata")
    all_data = []
    
    # 遍历所有城市CSV文件
    for csv_file in data_dir.glob("*.csv"):
        try:
            # 读取城市数据
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # 添加城市名称列
            city_name = csv_file.stem
            df['city'] = city_name
            
            all_data.append(df)
            print(f"已读取 {city_name}: {len(df)} 条记录")
            
        except Exception as e:
            print(f"读取 {csv_file} 失败: {e}")
    
    if all_data:
        # 合并所有数据
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # 保存合并后的数据
        output_file = "data/china_city_attraction_details.csv"
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\n数据合并完成!")
        print(f"总记录数: {len(merged_df)}")
        print(f"输出文件: {output_file}")
        
        # 显示数据统计
        print(f"\n数据统计:")
        print(f"- 城市数量: {len(all_data)}")
        print(f"- 总景点数: {len(merged_df)}")
        print(f"- 平均每城市景点数: {len(merged_df) // len(all_data)}")
        
        return merged_df
    else:
        print("没有找到可用的数据文件")
        return None

if __name__ == "__main__":
    merge_city_data()
