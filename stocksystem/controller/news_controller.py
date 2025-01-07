from flask import Blueprint, request, jsonify
from service.news_service import NewsService
import asyncio
news_blueprint = Blueprint('news', __name__)


# 假设这是你的20个行业标签，中英文一一对应
industry_tags = {
    "科技": "Technology",
    "金融": "Finance",
    "医疗": "Healthcare",
    "教育": "Education",
    "能源": "Energy",
    "制造": "Manufacturing",
    "零售": "Retail",
    "房地产": "Real Estate",
    "交通": "Transportation",
    "娱乐": "Entertainment",
    "旅游": "Tourism",
    "农业": "Agriculture",
    "电信": "Telecommunications",
    "媒体": "Media",
    "环保": "Environmental Protection",
    "食品": "Food",
    "汽车": "Automotive",
    "服装": "Apparel",
    "建筑": "Construction",
    "化工": "Chemical"
}


@news_blueprint.route('/add', methods=['POST'])
def add_news():
    """
    添加新闻
    """
    data = request.json
    title = data.get('title')
    url = data.get('url')
    content = data.get('content')
    publishdate = data.get('publishdate')
    sourceid = data.get('sourceid')
    industryid = data.get('industryid')
    sentimentid = data.get('sentimentid')
    stockid = data.get('stockid')

    if not title:
        return jsonify({"success": False, "message": "标题不能为空"}), 400

    result = NewsService.add_news(title, url, content, publishdate, sourceid, industryid, sentimentid, stockid)
    return jsonify(result)


@news_blueprint.route('/<int:newsid>', methods=['GET'])
def get_news(newsid):
    """
    获取单条新闻
    """
    news = NewsService.get_news_by_id(newsid)
    if news:
        return jsonify(news)
    else:
        return jsonify({"success": False, "message": "新闻不存在"}), 404


@news_blueprint.route('/all', methods=['GET'])
def get_all_news():
    """
    获取所有新闻
    """
    news_list = NewsService.get_all_news(1,5)

    return news_list


@news_blueprint.route('/delete/<int:newsid>', methods=['DELETE'])
def delete_news(newsid):
    """
    删除新闻
    """
    result = NewsService.delete_news(newsid)
    return jsonify(result)


@news_blueprint.route('/update', methods=['POST'])
def update_news():
    """
    更新新闻
    """
    data = request.json
    newsid = data.get('newsid')
    title = data.get('title')
    url = data.get('url')
    content = data.get('content')
    publishdate = data.get('publishdate')
    sourceid = data.get('sourceid')
    industryid = data.get('industryid')
    sentimentid = data.get('sentimentid')
    stockid = data.get('stockid')

    if not newsid:
        return jsonify({"success": False, "message": "newsid 必须提供"}), 400
    result = NewsService.update_news(newsid, title, url, content, publishdate, sourceid, industryid, sentimentid, stockid)
    return jsonify(result)


@news_blueprint.route('/analyze', methods=['POST'])
async def analyze_news():
    """
    根据行业标签获取新闻并分析
    """
    data = request.json
    keyword = data.get('keyword')  # 用户选择的行业标签
    if not keyword:
        return jsonify({"success": False, "message": "行业标签不能为空"}), 400

    result = await NewsService.fetch_and_analyze_news(keyword)
    return jsonify(result)



@news_blueprint.route('/search', methods=['GET'])
def search_news():
    """
    根据行业和情感标签搜索新闻，支持分页和排序

    请求参数（均为可选）：
    - industryid: 行业ID，整数类型。如果不传递，则不对行业进行筛选。
    - sentiment: 情感标签，字符串类型（如 "正面", "负面", "中性"）。如果不传递，则不对情感标签进行筛选。
    - page: 当前页码，整数类型，默认为 1。
    - per_page: 每页显示的新闻数量，整数类型，默认为 10。
    - sort_by: 排序字段，字符串类型，默认为 "publishdate"（按发布时间排序）。
    - order: 排序顺序，字符串类型，默认为 "desc"（降序）。可选值为 "asc"（升序）或 "desc"（降序）。

    返回值：
    - success: 布尔值，表示请求是否成功。
    - data: 包含新闻数据的列表，每个新闻对象包含以下字段：
        - newsid: 新闻ID。
        - title: 新闻标题。
        - url: 新闻链接。
        - content: 新闻内容。
        - publishdate: 新闻发布时间，格式为 "YYYY-MM-DD"。
        - sourceid: 新闻来源ID。
        - industryid: 行业ID。
        - sentimentid: 情感ID。
        - stockid: 股票ID。
        - sentiment: 情感标签（如 "正面", "负面", "中性"）。
    - total: 符合条件的新闻总数。
    - page: 当前页码。
    - per_page: 每页显示的新闻数量。

    示例请求：
    - 搜索行业ID为1且情感标签为"正面"的新闻，按发布时间降序排列，返回第1页，每页10条：
      GET /search?industryid=1&sentiment=正面&page=1&per_page=10&sort_by=publishdate&order=desc

    - 搜索所有新闻，按发布时间降序排列，返回第2页，每页20条：
      GET /search?page=2&per_page=20&sort_by=publishdate&order=desc
    """
    # 从请求参数中获取数据
    industryid = request.args.get('industryid', type=int)  # 行业ID
    sentiment = request.args.get('sentiment')  # 情感标签（如 "正面", "负面", "中性"）
    page = request.args.get('page', default=1, type=int)  # 当前页码，默认为 1
    per_page = request.args.get('per_page', default=10, type=int)  # 每页显示的新闻数量，默认为 10
    sort_by = request.args.get('sort_by', default="publishdate")  # 排序字段，默认为 "publishdate"
    order = request.args.get('order', default="desc")  # 排序顺序，默认为 "desc"

    # 调用服务层方法
    result = NewsService.search_news_by_industry_and_sentiment(
        industryid=industryid,
        sentiment=sentiment,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order
    )

    # 返回结果
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@news_blueprint.route('/analyze-all', methods=['POST'])
async def analyze_all_news():
    """
    批量处理所有预定义的行业标签
    """
    # 获取所有预定义的行业标签
    keywords = list(industry_tags.values())

    # 并发处理每个标签
    tasks = [NewsService.fetch_and_analyze_news(keyword) for keyword in keywords]
    results = await asyncio.gather(*tasks)

    # 返回结果
    return jsonify({
        "success": True,
        "data": results
    })
