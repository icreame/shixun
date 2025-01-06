from model.sentiment import Sentiment,db
from sqlalchemy.exc import SQLAlchemyError


class SentimentService:

    @staticmethod
    def add_sentiment(sentiment, score):
        try:
            new_sentiment = Sentiment(sentiment=sentiment, score=score)
            db.session.add(new_sentiment)
            db.session.commit()
            return {"id": new_sentiment.sentimentid, "sentiment": new_sentiment.sentiment,
                    "score": new_sentiment.score}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_all_sentiments():
        print("sentiments")
        try:

            # [0106修改去除 distinct() ]
            sentiments = Sentiment.query.with_entities(Sentiment.sentiment).distinct().all()
            sentiment_list =[{
                "sentiment": sent.sentiment,
           }for sent in sentiments]
            return sentiment_list
        except SQLAlchemyError as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_sentiment_by_id(sentimentid):
        try:
            sent = Sentiment.query.get(sentimentid)
            return sent
        except SQLAlchemyError as e:
            return {"success": False, "message": "情感属性不存在"}

    @staticmethod
    def update_sentiment(sentimentid, sentiment=None, score=None):
        try:
            sentiment_record = Sentiment.query.get(sentimentid)

            if sentiment_record:    # 若更新了sentiment 和 score 就更新
                if sentiment is not None:
                    sentiment_record.sentiment = sentiment
                if score is not None:
                    sentiment_record.score = score

                db.session.commit()
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
