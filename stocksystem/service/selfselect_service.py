from model.selfselect import SelfSelect,db
from model.stock import  Stock
from model.industry import Industry

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
        stock_list = []
        for select in selfselects:
            stocks_item = {
                "userid":userid
            }

            if select.stockid:
                stock = Stock.query.get(select.stockid)
                stocks_item["stockname"] = stock.stockname if stock else None
                stocks_item["stockcode"]=stock.stockcode if stock else None
            stock_list.append(stocks_item)
        return stock_list  # 返回股票id的列表

    @staticmethod
    def remove_self_select(userid, stockid):
        selfselect = SelfSelect.query.filter_by(userid=userid, stockid=stockid).first()
        if not selfselect:
            return {"success": False, "message": "该股票不在您的自选股中"}

        db.session.delete(selfselect)
        db.session.commit()

        return {"success": True, "message": "股票已从自选股中移除"}
