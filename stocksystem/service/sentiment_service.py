from model.sentiment import Sentiment,db

class SentimentService:

    @staticmethod
    def add_sentiment(sentimenttype, description=None):
        new_sentiment = Sentiment(sentimenttype=sentimenttype, description=description)
        db.session.add(new_sentiment)
        db.session.commit()
        return {"id": new_sentiment.sentimentid, "type": new_sentiment.sentimenttype, "description": new_sentiment.description}

    @staticmethod
    def get_all_sentiments():
        return Sentiment.query.all()

    @staticmethod
    def get_sentiment_by_id(sentimentid):
        return Sentiment.query.get(sentimentid)

    @staticmethod
    def update_sentiment(sentimentid, sentimenttype=None, description=None):
        sentiment = Sentiment.query.get(sentimentid)
        if sentiment:
            if sentimenttype:
                sentiment.sentimenttype = sentimenttype
            if description:
                sentiment.description = description
            db.session.commit()
            return {"success": True, "message": "情感更新成功"}
        else:
            return {"success": False, "message": "情感不存在"}

    @staticmethod
    def delete_sentiment(sentimentid):
        sentiment = Sentiment.query.get(sentimentid)
        if sentiment:
            db.session.delete(sentiment)
            db.session.commit()
            return {"success": True, "message": "情感已删除"}
        else:
            return {"success": False, "message": "情感不存在"}
