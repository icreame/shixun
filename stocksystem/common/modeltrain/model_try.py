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
            # 查询新闻数据 （目前只查找一条）
            query = "SELECT newsid, content FROM news"
            cursor.execute(query)
            # 获取所有新闻内容
            news_data = cursor.fetchall()
            print(news_data)
            return news_data
    finally:
        connection.close()


# 插入的数据格式为{'positive': 0.7444491982460022, 'negative': 0.255550742149353}
def insert_sentiment_to_db(sentiment_data):
    # 连接到数据库
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 插入情感分析结果到sentiment表
            query = """  
                            INSERT INTO sentiment (positive, negative)  
                            VALUES (%s, %s)  
                        """
            positive = sentiment_data['positive']
            negative = sentiment_data['negative']
            cursor.execute(query, (positive, negative))
            connection.commit()
            print(f"Inserted record with positive={positive}, negative={negative}")
    finally:
        connection.close()


# 用来检测是否插入成功，但是还没用过
def check_inserted_data(newsid, positive, negative):
    # 连接到数据库
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 查询新插入的记录
            query = "SELECT positive, negative FROM sentiment WHERE newsid = %s ORDER BY sentimentid DESC LIMIT 1"
            cursor.execute(query, (newsid,))
            result = cursor.fetchone()
            if result:
                inserted_positive, inserted_negative = result
                assert abs(inserted_positive - positive) < 1e-6, "Inserted positive value does not match"
                assert abs(inserted_negative - negative) < 1e-6, "Inserted negative value does not match"
                print("Data insertion successful.")
            else:
                print("No record found for the inserted data.")
    finally:
        connection.close()


def db_to_sentiment():
    # 初始化情感分析管道
    semantic_cls = pipeline(Tasks.text_classification, 'damo/nlp_structbert_sentiment-classification_chinese-base')

    # 从数据库中读取新闻数据
    news_data = get_news_from_db()

    for newsid, content in news_data:
        # 进行情感分析
        result = semantic_cls(input=content)
        # print(f"新闻ID: {newsid}, 内容: {content}")
        print(f"情感分析结果: {result}")

        # 将情感分析结果插入数据库
        sentiment_data = {
            'positive': result['scores'][0],
            'negative': result['scores'][1]
        }
        print(sentiment_data)
        try:
            insert_sentiment_to_db(sentiment_data)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=FutureWarning)
    db_to_sentiment()
    # sentiment_data = {
    #     'scores': [0.8, 0.2],
    #     'labels': ['positive', 'negative']
    # }
    # newsid = 1
    # insert_sentiment_to_db(sentiment_data)
