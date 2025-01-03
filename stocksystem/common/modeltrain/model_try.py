import pymysql
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import warnings

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'shixun',
    'password': '123456',
    'database': 'stocksystem',
    'charset': 'utf8mb4'
}


def get_news_from_db():
    # 连接到数据库
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 查询新闻数据
            query = "SELECT newsid, content FROM news"
            cursor.execute(query)
            # 获取所有新闻内容
            news_data = cursor.fetchall()
            return news_data
    finally:
        connection.close()


def insert_sentiment_to_db(sentiment_data, newsid):
    # 连接到数据库
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 插入情感分析结果到sentiment表
            query = """
                INSERT INTO sentiment (sentimenttype, description)
                VALUES (%s, %s)
            """
            for sentiment_type, score in sentiment_data.items():
                cursor.execute(query, (sentiment_type, str(score)))
            connection.commit()
    finally:
        connection.close()


def test():
    # 初始化情感分析管道
    semantic_cls = pipeline(Tasks.text_classification, 'damo/nlp_structbert_sentiment-classification_chinese-base')

    # 从数据库中读取新闻数据
    news_data = get_news_from_db()

    for newsid, content in news_data:
        # 进行情感分析
        result = semantic_cls(input=content)
        print(f"新闻ID: {newsid}, 内容: {content}")
        print(f"情感分析结果: {result}")

        # 将情感分析结果插入数据库
        sentiment_data = {
            '正面': result['scores'][0],
            '负面': result['scores'][1]
        }
        insert_sentiment_to_db(sentiment_data, newsid)


if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=FutureWarning)
    test()
