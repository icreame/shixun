import pandas as pd
import chardet
import pymysql


def analysis():
    csv_file = 'D:\\Python-program\\StockCrawler\\shixun\\stocksystem\\news_data\\板块数据-1-utf8.csv'
    # 使用chardet来识别url
    with open(csv_file, 'rb') as f:
        file_content = f.read()
        result = chardet.detect(file_content)
    encoding = result['encoding']
    df = pd.read_csv(csv_file, usecols=[0], names=['行业'])
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
                sql = "INSERT INTO industry (industryname) VALUES (%s)"
                cursor.execute(sql, (row['行业']))

        connection.commit()

    finally:
        connection.close()


if __name__ == '__main__':
    analysis()
