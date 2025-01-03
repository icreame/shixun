import pandas as pd
import chardet
from pathlib import Path


def analysis():
    csv_file = 'D:\\Python-program\\StockCrawler\\shixun\\stocksystem\\news_data\\大盘.csv'
    # 使用chardet来识别url
    with open(csv_file, 'rb') as f:
        file_content = f.read()
        result = chardet.detect(file_content)
    encoding = result['encoding']
    # print(encoding)
    df = pd.read_csv(csv_file, usecols=[1, 2, 3], names=['url', 'market_name', 'news'], encoding=encoding)
    print(df)


if __name__ == '__main__':
    analysis()
