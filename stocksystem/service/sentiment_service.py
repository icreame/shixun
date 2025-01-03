from model.sentiment import Sentiment,db
from sqlalchemy.exc import SQLAlchemyError

class SentimentService:

    @staticmethod
    def add_sentiment(sentimenttype, description=None):
        try:
            new_sentiment = Sentiment(sentimenttype=sentimenttype, description=description)
            db.session.add(new_sentiment)
            db.session.commit()
            return {"id": new_sentiment.sentimentid, "type": new_sentiment.sentimenttype,
                    "description": new_sentiment.description}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_all_sentiments():
        try:
            return Sentiment.query.all()
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_sentiment_by_id(sentimentid):
        try:
            return Sentiment.query.get(sentimentid)
        except SQLAlchemyError as e:
            return {"success": False, "message": "情感属性不存在"}

    @staticmethod
    def update_sentiment(sentimentid, sentimenttype=None, description=None):
        try:
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
