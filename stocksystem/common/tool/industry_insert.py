import pymysql

# 数据库连接配置
conn = pymysql.connect(host='localhost', user='shixun', password='123456', database='stocksystem', charset='utf8mb4')
cursor = conn.cursor()

# 读取 CSV 文件
import pandas as pd

# 文件路径
df = pd.read_csv('D:\\Python-program\\StockCrawler\\shixun\\stocksystem\\news_data\\板块数据-3-utf8.csv')
# 清洗数据，移除包含nan值的行
df_cleaned = df.dropna(subset=['行业'])

# 遍历每个行业名，插入前检查是否存在
for industry in df_cleaned['行业']:
    # 检查行业名是否已经存在
    cursor.execute("SELECT COUNT(*) FROM industry WHERE industryname = %s", (industry,))
    result = cursor.fetchone()

    # 如果不存在，则插入该行业名
    if result[0] == 0:
        cursor.execute("INSERT INTO industry (industryname) VALUES (%s)", (industry,))
        conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()

print("数据插入完成！")
