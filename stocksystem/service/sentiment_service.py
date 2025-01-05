from model.sentiment import Sentiment,db
from sqlalchemy.exc import SQLAlchemyError


class SentimentService:

    @staticmethod
    def add_sentiment(positive,negative):
        try:
            new_sentiment = Sentiment(positive=positive,negative=negative)
            db.session.add(new_sentiment)
            db.session.commit()
            return {"id": new_sentiment.sentimentid, "positive": new_sentiment.positive,
                    "negative": new_sentiment.negative}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_all_sentiments():
        print("sentiments")
        try:
            # 使用distinct()去重
            sentiments = Sentiment.query.with_entities(Sentiment.sentiment).distinct().all()
            sentiment_list =[{
                # "sentimentid": sent.sentimentid,
                # "positive": sent.positive,
                # "negative": sent.negative,
                "sentiment": sent.sentiment
            }for sent in sentiments]
            return sentiment_list
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_sentiment_by_id(sentimentid):
        try:
            sent=Sentiment.query.get(sentimentid)
            return sent
        except SQLAlchemyError as e:
            return {"success": False, "message": "情感属性不存在"}

    @staticmethod
    def update_sentiment(sentimentid, positive=0, negative=0):
        try:
            sentiment = Sentiment.query.get(sentimentid)
            if sentiment:
                if positive:
                    sentiment.positive = positive
                if negative:
                    sentiment.negative = negative
                db.session.commit()
                return {"success": True, "message": "情感更新成功"}
            else:
                return {"success": False, "message": "情感不存在"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_sentiment(sentimentid):
        try:
            sentiment = Sentiment.query.get(sentimentid)
            if sentiment:
                db.session.delete(sentiment)
                db.session.commit()
                return {"success": True, "message": "情感已删除"}
            else:
                return {"success": False, "message": "情感不存在"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
