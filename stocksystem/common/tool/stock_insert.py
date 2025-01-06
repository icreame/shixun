import pymysql

# 数据库连接配置
conn = pymysql.connect(host='localhost', user='root', password='947400', database='stocksystem', charset='utf8mb4')
cursor = conn.cursor()

# 读取 CSV 文件
import pandas as pd

# 文件路径
df = pd.read_csv('D:\\learning\\寒假实训\\shixun\stocksystem\\news_data\\个股数据.csv')

# 清洗数据，移除包含 NaN 的行
df_cleaned = df.dropna(subset=['股票代码', '股票名称','所属行业'])

insert_data = []
stockprice=0
# 遍历数据
for _, row in df_cleaned.iterrows():
    code = row['股票代码']
    name = row['股票名称']
    industry_name = row['所属行业']

    # 获取 industryid
    cursor.execute("SELECT industryid FROM industry WHERE industryname = %s", (industry_name,))
    industry_result = cursor.fetchone()

    # 如果行业存在，获取其 industryid
    if industry_result:
        industryid = industry_result[0]

        # 检查股票是否已存在
        cursor.execute("SELECT COUNT(*) FROM stock WHERE stockid = %s", (code,))
        stock_exists = cursor.fetchone()

        if stock_exists[0] == 0:  # 如果股票不存在，添加到插入列表
            insert_data.append((code, name, stockprice, industryid))
    else:
        print(f"未找到行业: {industry_name}，请检查行业表中的数据。")

# 批量插入
if insert_data:
    cursor.executemany(
        "INSERT INTO stock (stockid, stockname, stockprice, industryid) VALUES (%s, %s, %s, %s)",
        insert_data
    )
    conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()

print("数据插入完成！")