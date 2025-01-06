from model.selfselect import SelfSelect,db

class SelfSelectService:

    @staticmethod
    def add_self_select(userid, stockid):
        try:
            db.session.add(new_selfselect)
            db.session.commit()
            return {"success": True, "message": "股票已添加到自选股"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"自选股添加失败: {str(e)}"}

    @staticmethod
    def get_user_self_selects(userid):
        selfselects = SelfSelect.query.filter_by(userid=userid).all()
        stock_list = [{"stock_id": stock.stockid, "stockname": stock.stockname,
                       "stockprice": stock.stockprice, "industry": stock.industry.industryname}
                      for stock in selfselects]
        return stock_list  # 返回股票id的列表

    @staticmethod
    def remove_self_select(userid, stockid):
        selfselect = SelfSelect.query.filter_by(userid=userid, stockid=stockid).first()
        if not selfselect:
            return {"success": False, "message": "该股票不在您的自选股中"}

        db.session.delete(selfselect)
        db.session.commit()

        return {"success": True, "message": "股票已从自选股中移除"}
