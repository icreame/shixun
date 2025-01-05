import pymysql

# 数据库连接配置
conn = pymysql.connect(host='localhost', user='root', password='947400', database='stocksystem', charset='utf8mb4')
cursor = conn.cursor()

# 读取 CSV 文件
import pandas as pd

# 文件路径
df = pd.read_csv('D:\\learning\\寒假实训\\shixun\\stocksystem\\news_data\\板块数据-1-utf8.csv')

# 清洗数据，移除包含 NaN 的行
df_cleaned = df.dropna(subset=['标题', '内容', 'url'])

# 使用批量插入减少对数据库的压力
insert_data = []

# 遍历数据
for _, row in df_cleaned.iterrows():
    title = row['标题']
    content = row['内容']
    url = row['url']

    # 检查标题对应的 URL 是否已经存在
    cursor.execute("SELECT COUNT(*) FROM news WHERE url = %s", (url,))
    result = cursor.fetchone()

    # 如果 URL 不存在，准备插入
    if result[0] == 0:
        insert_data.append((title, content, url))

# 批量插入
if insert_data:
    cursor.executemany("INSERT INTO news (title, content, url) VALUES (%s, %s, %s)", insert_data)
    conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()

print("数据插入完成！")