from flask import logging
from model.selfselect import SelfSelect,db
from model.stock import  Stock
from datetime import datetime,timedelta
from model.industry import Industry
import tushare as ts
import pandas as pd

ts.set_token('b7378a5c379a258bd7f96c9d3c411d6484b82d0ff3ce312f720abc9c')
pro = ts.pro_api()

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
                    df1 = pro.daily_basic(ts_code=stock.stockcode, trade_date=datetime.now().strftime('%Y%m%d'))
                    df = ts.realtime_list(src='dc')
                    pd.set_option('display.max_columns', 1000)
                    pd.set_option('display.width', 1000)
                    pd.set_option('display.max_colwidth', 1000)

                    stocks_item["volume"] = df['VOLUME'].iloc[0]    # 成交量(单位：手)
                    stocks_item["close"] = df['CLOSE'].iloc[0]
                    stocks_item["pct_change"]=df['PCT_CHANGE'].iloc[0]  # 涨跌幅
                    stocks_item['5min']=df['5MIN'].iloc[0]  # 5分钟涨幅
                    stocks_item["totoal_mv"] = df1['total_mv'].iloc[0]

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
