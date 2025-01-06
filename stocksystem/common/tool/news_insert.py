import pymysql

# 数据库连接配置
conn = pymysql.connect(host='localhost', user='root', password='947400', database='stocksystem', charset='utf8mb4')
cursor = conn.cursor()

# 读取 CSV 文件
import pandas as pd

# 文件路径
df = pd.read_csv('D:\\learning\\寒假实训\\shixun\\stocksystem\\news_data\\板块数据-3-utf8.csv')

# 清洗数据，移除包含 NaN 的行
df_cleaned = df.dropna(subset=['标题', '内容', 'url'])

# 使用批量插入减少对数据库的压力
insert_data = []

# 遍历数据
for _, row in df_cleaned.iterrows():
    title = row['标题']
    content = row['内容']
    url = row['url']
    industry_name=row['行业']

    # 获取 industryid
    cursor.execute("SELECT industryid FROM industry WHERE industryname = %s", (industry_name,))
    industry_result = cursor.fetchone()

    # 如果行业存在，获取其 industryid
    if industry_result:
        industryid = industry_result[0]

        # 检查股票是否已存在
        cursor.execute("SELECT COUNT(*) FROM news WHERE title = %s", (title,))
        news_exists = cursor.fetchone()

        if news_exists[0] == 0:  # 如果股票不存在，添加到插入列表
            insert_data.append((title,content,url,industryid))
    else:
        print(f"未找到行业: {industry_name}，请检查行业表中的数据。")

# 批量插入
if insert_data:
    cursor.executemany("INSERT INTO news (title, content, url, industryid) VALUES (%s, %s, %s,%s)", insert_data)
    conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()

print("数据插入完成！")