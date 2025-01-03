import pymysql

db_config = {
    'host': 'localhost',
    'user': 'shixun',
    'password': '123456',
    'database': 'stocksystem',
    'charset': 'utf8mb4'
}


def get_sentimentid_by_newsid(newsid):
    """
    根据 newsid 查找对应的 sentimentid。

    Args:
        newsid (int): 新闻的 ID。

    Returns:
        int: 对应的情感分析结果的 ID。
    """
    # 连接到数据库
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # 查询 sentiment 表,获取最新插入的 sentimentid
            query = "SELECT sentimentid FROM sentiment ORDER BY sentimentid ASC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    finally:
        connection.close()


def update_news_sentimentid(newsid):
    """
    根据 newsid 更新 news 表中的 sentimentid 字段。

    Args:
        newsid (int): 新闻的 ID。
    """
    # 连接到数据库
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # 获取对应的 sentimentid
            sentimentid = get_sentimentid_by_newsid(newsid)

            # 更新 news 表中的 sentimentid 字段
            query = "UPDATE news SET sentimentid = %s WHERE newsid = %s"
            cursor.execute(query, (sentimentid, newsid))
            connection.commit()

            print(f"Updated sentimentid for newsid={newsid} to {sentimentid}")
    finally:
        connection.close()

# 查询单个新闻的情感指数，参数为新闻的id
def get_sentimentid_by_newsid(newsid):
    """
    根据 newsid 查找对应的 sentimentid。

    Args:
        newsid (int): 新闻的 ID。

    Returns:
        int: 对应的情感分析结果的 ID。
    """
    # 连接到数据库
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # 查询 sentiment 表,获取最新插入的 sentimentid
            query = "SELECT sentimentid FROM sentiment ORDER BY sentimentid ASC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    finally:
        connection.close()


# 查询所有新闻的情感指数
def get_all_news_with_sentiment():
    """
    查询所有新闻内容及其对应的情感数据。

    Returns:
        list: 包含所有新闻内容及情感数据的字典列表。
    """
    # 连接到数据库
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 联合查询语句
            query = """
            SELECT 
                n.newsid,
                n.content, 
                s.positive, 
                s.negative
            FROM 
                news n
            JOIN 
                sentiment s
            ON 
                n.sentimentid = s.sentimentid
            """
            # 执行查询
            cursor.execute(query)
            results = cursor.fetchall()

            # 将结果转换为字典列表
            data = []
            for row in results:
                data.append({
                    "newsid": row[0],
                    "content": row[1],
                    "positive": row[2],
                    "negative": row[3],
                })

            return data
    finally:
        connection.close()


def map_sentiment_to_news():
    """
    将 sentiment 表的 sentimentid 按照一一映射插入到 news 表的 sentimentid 字段。
    """
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 查询 news 表和 sentiment 表中的所有 ID
            query_news = "SELECT newsid FROM news ORDER BY newsid ASC"
            query_sentiment = "SELECT sentimentid FROM sentiment ORDER BY sentimentid ASC"

            cursor.execute(query_news)
            news_ids = cursor.fetchall()

            cursor.execute(query_sentiment)
            sentiment_ids = cursor.fetchall()

            # 确保 news 和 sentiment 数量相同
            if len(news_ids) != len(sentiment_ids):
                print("Mismatch in the number of news and sentiment records.")
                return

            # 一一映射更新 news 表的 sentimentid 字段
            update_query = "UPDATE news SET sentimentid = %s WHERE newsid = %s"
            for news, sentiment in zip(news_ids, sentiment_ids):
                cursor.execute(update_query, (sentiment[0], news[0]))

            # 提交更改
            connection.commit()
            print("Successfully mapped sentimentid to news.")
    finally:
        connection.close()


if __name__ == '__main__':
    # 查询所有新闻及其情感数据
    news_with_sentiment = get_all_news_with_sentiment()
    for record in news_with_sentiment:
        print(f"News ID: {record['newsid']}")
        print(f"Content: {record['content']}")
        print(f"Positive: {record['positive']}")
        print(f"Negative: {record['negative']}")
        print("-" * 50)

