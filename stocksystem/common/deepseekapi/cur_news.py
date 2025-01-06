from gdeltdoc import GdeltDoc, Filters
import pandas as pd
import urllib.parse
import time
import os
# 定义关键字列表
keywords = [
    "Natural Gas", "Alcoholic Beverage Industry", "Jewelry and Accessories",
    "Coal Industry", "Shipping and Ports", "Port Shipping", "Port Aviation",
    "Textiles and Apparel", "Railways and Highways", "Tourism and Hotels",
    "Mining Industry", "Decoration and Renovation", "Department Stores and Retail",
    "Food and Beverage", "Petroleum Industry", "Precious Metals",
    "Non-Metallic Materials", "Beauty and Personal Care", "Public Utilities",
    "Decorative Building Materials"
]
# 获取当前代码文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 指定保存目录（相对路径）
output_directory = os.path.join(current_dir, "data_collection")

# 初始化GdeltDoc
gd = GdeltDoc()

# 遍历每个关键字
for keyword in keywords:
    # 对关键字进行URL编码
    encoded_keyword = urllib.parse.quote(keyword)

    # 设置过滤器
    f = Filters(
        keyword=encoded_keyword,
        start_date="2024-12-03",
        end_date="2025-01-06",
        num_records=150,
        country="China",
        language="Chinese"
    )
    try:
        # 调用API获取数据
        articles = gd.article_search(f)

        # 检查是否获取到数据
        if not articles.empty:
            # 将数据保存到CSV文件
            filename = f"{keyword.replace(' ', '_').lower()}_news.csv"
            # 指定完整文件路径
            filepath = os.path.join(output_directory, filename)

            df = pd.DataFrame(articles)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"关键字 '{keyword}' 查询成功，数据已保存到 {filepath}")
        else:
            print(f"关键字 '{keyword}' 未能获取任何数据，请检查查询参数或网络连接。")
    except Exception as e:
        print(f"关键字 '{keyword}' 查询失败，错误信息: {e}")

    # 增加延迟以避免触发API限制
    time.sleep(5)
