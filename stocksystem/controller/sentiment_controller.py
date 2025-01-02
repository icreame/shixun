from flask import Blueprint, request, jsonify
from service.sentiment_service import SentimentService

sentiment_blueprint = Blueprint('sentiment', __name__)


@sentiment_blueprint.route('/add', methods=['POST'])
def add_sentiment():
    """
    添加情感
    """
    data = request.json
    sentimenttype = data.get('sentimenttype')
    description = data.get('description')

    if not sentimenttype:
        return jsonify({"success": False, "message": "情感类别不能为空"}), 400

    sentiment = SentimentService.add_sentiment(sentimenttype, description)
    return jsonify({"success": True, "message": "情感已添加", "sentiment": sentiment})


@sentiment_blueprint.route('/all', methods=['GET'])
def get_all_sentiments():
    """
    获取所有情感
    """
    sentiments = SentimentService.get_all_sentiments()
    return jsonify({"success": True, "sentiments": [sentiment.sentimenttype for sentiment in sentiments]})


@sentiment_blueprint.route('/<int:sentimentid>', methods=['GET'])
def get_sentiment_by_id(sentimentid):
    """
    获取单个情感
    """
    sentiment = SentimentService.get_sentiment_by_id(sentimentid)
    if sentiment:
        return jsonify({"success": True, "sentiment": {"id": sentiment.sentimentid, "type": sentiment.sentimenttype, "description": sentiment.description}})
    else:
        return jsonify({"success": False, "message": "情感不存在"}), 404


@sentiment_blueprint.route('/update', methods=['PUT'])
def update_sentiment():
    """
    更新情感
    """
    data = request.json
    sentimentid = data.get('sentimentid')
    sentimenttype = data.get('sentimenttype')
    description = data.get('description')

    if not sentimentid:
        return jsonify({"success": False, "message": "sentimentid不能为空"}), 400

    result = SentimentService.update_sentiment(sentimentid, sentimenttype, description)
    return jsonify(result)


@sentiment_blueprint.route('/delete/<int:sentimentid>', methods=['DELETE'])
def delete_sentiment(sentimentid):
    """
    删除情感
    """
    result = SentimentService.delete_sentiment(sentimentid)
    return jsonify(result)
