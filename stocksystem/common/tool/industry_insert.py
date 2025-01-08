import pymysql
import pandas as pd

# 数据库连接配置
conn = pymysql.connect(host='localhost', user='root', password='947400', database='stocksystem', charset='utf8mb4')
cursor = conn.cursor()

# 读取 CSV 文件
df = pd.read_csv("D:\\learning\\寒假实训\\shixun\\stocksystem\\news_data\\个股数据.csv")

# 清洗数据，移除包含nan值的行
df_cleaned = df.dropna(subset=['所属行业'])

# 遍历每个行业名，插入前检查是否存在，并获取 industryid
for index, row in df_cleaned.iterrows():
    industry = row['所属行业']
    stockcode = row['股票代码']
    stockname = row['股票名称']

    # 检查行业名是否已经存在
    cursor.execute("SELECT industryid FROM industry WHERE industryname = %s", (industry,))
    result = cursor.fetchone()

    # 如果行业名不存在，插入该行业，并获取 industryid
    if result is None:
        cursor.execute("INSERT INTO industry (industryname) VALUES (%s)", (industry,))
        conn.commit()  # 提交插入操作
        cursor.execute("SELECT industryid FROM industry WHERE industryname = %s", (industry,))
        result = cursor.fetchone()  # 获取插入后的 industryid

    # 获取 industryid
    industryid = result[0]

    # 插入股票数据到 stock 表
    cursor.execute("""
        INSERT INTO stock (stockcode, stockname, industryid) 
        VALUES (%s, %s, %s)
        """, (stockcode, stockname, industryid))
    conn.commit()  # 提交插入操作

# 关闭数据库连接
cursor.close()
conn.close()
