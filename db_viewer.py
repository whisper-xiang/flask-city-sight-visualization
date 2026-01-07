#!/usr/bin/env python3
"""
数据库查看工具
用于在HexHub中查看SQLite数据库内容
"""

import sqlite3
import pandas as pd
from pathlib import Path

def view_database():
    """查看数据库内容"""
    db_path = Path("instance/city_attractions.db")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📊 数据库概览")
        print("=" * 50)
        print(f"数据库文件: {db_path}")
        print(f"文件大小: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
        print()
        
        for table in tables:
            table_name = table[0]
            print(f"📋 表: {table_name}")
            print("-" * 30)
            
            # 获取记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"记录数: {count}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("字段:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # 显示前几条数据
            if table_name == 'attractions':
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                print("\n前5条数据:")
                for i, row in enumerate(rows, 1):
                    print(f"  {i}. {row[1]} - {row[13]} ({row[14]})")  # name, province, city
            
            elif table_name == 'users':
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                print("\n用户数据:")
                for row in rows:
                    print(f"  - {row[1]} ({row[2]})")
            
            print()
        
        # 数据统计
        print("📈 数据统计")
        print("-" * 30)
        
        # 景点统计
        cursor.execute("""
            SELECT province, COUNT(*) as count 
            FROM attractions 
            WHERE province != '' 
            GROUP BY province 
            ORDER BY count DESC 
            LIMIT 10
        """)
        provinces = cursor.fetchall()
        print("景点数量前10的省份:")
        for province, count in provinces:
            print(f"  {province}: {count}")
        
        print()
        
        # 评分统计
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN rating >= 4.5 THEN '4.5-5.0'
                    WHEN rating >= 4.0 THEN '4.0-4.5'
                    WHEN rating >= 3.5 THEN '3.5-4.0'
                    WHEN rating >= 3.0 THEN '3.0-3.5'
                    ELSE '0-3.0'
                END as rating_range,
                COUNT(*) as count
            FROM attractions 
            GROUP BY rating_range 
            ORDER BY rating_range DESC
        """)
        ratings = cursor.fetchall()
        print("评分分布:")
        for rating_range, count in ratings:
            print(f"  {rating_range}: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")

def export_to_csv():
    """导出数据到CSV文件"""
    db_path = Path("instance/city_attractions.db")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 导出attractions表
        df_attractions = pd.read_sql_query("SELECT * FROM attractions", conn)
        df_attractions.to_csv("data/attractions_export.csv", index=False, encoding='utf-8-sig')
        print(f"✅ 景点数据已导出到: data/attractions_export.csv ({len(df_attractions)} 条记录)")
        
        # 导出users表
        df_users = pd.read_sql_query("SELECT * FROM users", conn)
        df_users.to_csv("data/users_export.csv", index=False, encoding='utf-8-sig')
        print(f"✅ 用户数据已导出到: data/users_export.csv ({len(df_users)} 条记录)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def search_attractions(keyword="", province="", city="", limit=10):
    """搜索景点"""
    db_path = Path("instance/city_attractions.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM attractions WHERE 1=1"
        params = []
        
        if keyword:
            query += " AND name LIKE ?"
            params.append(f"%{keyword}%")
        
        if province:
            query += " AND province LIKE ?"
            params.append(f"%{province}%")
        
        if city:
            query += " AND city LIKE ?"
            params.append(f"%{city}%")
        
        query += " ORDER BY rating DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        print(f"🔍 搜索结果 (找到 {len(results)} 条记录):")
        print("-" * 50)
        
        for i, row in enumerate(results, 1):
            print(f"{i}. {row[1]}")
            print(f"   📍 {row[13]} {row[14]} {row[15]}")  # province, city, district
            print(f"   ⭐ 评分: {row[7]}")
            print(f"   🎫 门票: {row[9]}")
            print(f"   ⏰ 建议游玩: {row[8]}")
            print(f"   🌸 最佳季节: {row[10]}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 搜索失败: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "view":
            view_database()
        elif command == "export":
            export_to_csv()
        elif command == "search":
            keyword = sys.argv[2] if len(sys.argv) > 2 else ""
            province = sys.argv[3] if len(sys.argv) > 3 else ""
            city = sys.argv[4] if len(sys.argv) > 4 else ""
            search_attractions(keyword, province, city)
        else:
            print("用法:")
            print("  python db_viewer.py view          # 查看数据库概览")
            print("  python db_viewer.py export         # 导出数据到CSV")
            print("  python db_viewer.py search 关键词   # 搜索景点")
    else:
        view_database()
