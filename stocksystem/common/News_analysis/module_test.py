import pandas as pd
import chardet
import pymysql


def analysis():
    csv_file = 'D:\\Python-program\\StockCrawler\\shixun\\stocksystem\\news_data\\板块数据-2-utf8.csv'
    # 使用chardet来识别url
    with open(csv_file, 'rb') as f:
        file_content = f.read()
        result = chardet.detect(file_content)
    encoding = result['encoding']
    df = pd.read_csv(csv_file, usecols=[1, 2, 3], names=['url', '标题', '内容'])
    print(df)

    connection = pymysql.connect(
        host='localhost',  # Your MySQL host
        user='shixun',  # Your MySQL username
        password='123456',  # Your MySQL password
        database='stocksystem',  # Your MySQL database name
        charset='utf8mb4'
    )

    try:
        with connection.cursor() as cursor:
            for _, row in df.iterrows():
                sql = "INSERT INTO news (url, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql, (row['url'], row['标题'], row['内容']))

        connection.commit()

    finally:
        connection.close()


if __name__ == '__main__':
    analysis()
