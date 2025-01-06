import pymysql

# 数据库连接配置
conn = pymysql.connect(host='localhost', user='shixun', password='123456', database='stocksystem', charset='utf8mb4')
cursor = conn.cursor()

# 读取 CSV 文件
import pandas as pd

# 文件路径
df = pd.read_csv('D:\\pycharmProject\\shixun\\stocksystem\\news_data\\个股数据.csv')
# 选择要写入的列
csv_to_db_mapping = {
    "股票名称": "stockname",
    "股票代码": "stockcode"
}

# 检查列是否存在
missing_columns = [col for col in csv_to_db_mapping.keys() if col not in df.columns]
if missing_columns:
    raise ValueError(f"The following required columns are missing in the CSV file: {missing_columns}")

# 创建对应的 DataFrame
selected_data = df[list(csv_to_db_mapping.keys())]
selected_data.rename(columns=csv_to_db_mapping, inplace=True)

# 写入数据库
table_name = "stock"

try:

    for index, row in selected_data.iterrows():
        sql = f"""
        INSERT INTO {table_name} (stockname, stockcode) 
        VALUES (%s, %s)
        """
        cursor.execute(sql, (row['stockname'], row['stockcode']))

    conn.commit()
    print(f"Successfully inserted {len(selected_data)} rows into '{table_name}'.")

except Exception as e:
    print(f"An error occurred: {e}")
    if conn:
        conn.rollback()

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

