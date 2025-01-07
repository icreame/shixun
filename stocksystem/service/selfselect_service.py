from flask import logging
from model.selfselect import SelfSelect,db
from model.stock import  Stock
from model.industry import Industry

class SelfSelectService:

    @staticmethod
    def add_self_select(userid, stockid):
        try:
            # 假设 new_selfselect 是一个自选股模型实例
            new_selfselect = SelfSelect(userid=userid, stockid=stockid)
            db.session.add(new_selfselect)
            db.session.commit()
            return {"success": True, "message": "股票已添加到自选股"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"自选股添加失败: {str(e)}"}

    @staticmethod
    def get_user_self_selects(userid):
        try:
            # 查询用户自选股
            # 显式使用 join 来连接 SelfSelect 和 Stock 表
            selfselects = db.session.query(SelfSelect, Stock).join(Stock, SelfSelect.stockid == Stock.stockid).filter(SelfSelect.userid == userid).all()
            selfselects = SelfSelect.query.filter_by(userid=userid).all()
            stock_list = []
            for select in selfselects:
                stocks_item = {
                    "userid": userid
                }

                if select.stockid:
                    stock = Stock.query.get(select.stockid)
                    stocks_item["stockname"] = stock.stockname if stock else None
                    stocks_item["stockcode"] = stock.stockcode if stock else None
                stock_list.append(stocks_item)
            return stock_list  # 返回股票id的列表
        except Exception as e:
            # 记录异常信息
            return {"success": False, "message": str(e)}
    @staticmethod
    def remove_self_select(userid, stockid):
        selfselect = SelfSelect.query.filter_by(userid=userid, stockid=stockid).first()
        if not selfselect:
            return {"success": False, "message": "该股票不在您的自选股中"}

        db.session.delete(selfselect)
        db.session.commit()

        return {"success": True, "message": "股票已从自选股中移除"}
