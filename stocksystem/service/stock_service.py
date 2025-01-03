# services/stock_service.py
from model.stock import Stock,db
from model.industry import Industry
from sqlalchemy.sql import text
import tushare as ts

# 设置你的 Tushare Token
ts.set_token('b7378a5c379a258bd7f96c9d3c411d6484b82d0ff3ce312f720abc9c')
pro = ts.pro_api()

class StockService:
    @staticmethod
    def create_stock(stockname, stockprice, industryid):
        try:
            industry = Industry.query.get(industryid)
            if not industry:
                return {"success": False, "message": "行业ID无效"}

            new_stock = Stock(stockname=stockname, stockprice=stockprice, industryid=industryid)
            db.session.add(new_stock)
            db.session.commit()
            return {"success": True, "message": "股票创建成功", "data": new_stock}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def update_stock(stock_id, stockname=None, stockprice=None, industryid=None):
        try:
            stock = Stock.query.get(stock_id)
            if not stock:
                return {"success": False, "message": "股票ID无效"}

            if stockname:
                stock.stockname = stockname
            if stockprice:
                stock.stockprice = stockprice
            if industryid:
                industry = Industry.query.get(industryid)
                if not industry:
                    return {"success": False, "message": "行业ID无效"}
                stock.industryid = industryid

            db.session.commit()
            return {"success": True, "message": "股票信息更新成功", "data": stock}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_stock(stock_id):
        try:
            stock = Stock.query.get(stock_id)
            if not stock:
                return {"success": False, "message": "股票ID无效"}

            db.session.delete(stock)
            db.session.commit()
            return {"success": True, "message": "股票删除成功"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_all_stocks():
        try:
            stocks = Stock.query.all()
            print(2)
            stock_list = [{"stock_id": stock.stockid, "stockname": stock.stockname,
                           "stockprice": stock.stockprice, "industry": stock.industry.industryname}
                          for stock in stocks]
            print(3)
            return {"success": True, "data": stock_list}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_stock_by_id(stock_id):
        try:
            stock = Stock.query.get(stock_id)
            if not stock:
                return {"success": False, "message": "股票ID无效"}

            stock_data = {
                "stock_id": stock.stockid,
                "stockname": stock.stockname,
                "stockprice": stock.stockprice,
                "industry": stock.industry.industryname
            }
            return {"success": True, "data": stock_data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_stocks_by_industry(industry_id):
        try:
            industry = Industry.query.get(industry_id)
            if not industry:
                return {"success": False, "message": "行业ID无效"}

            stocks = Stock.query.filter_by(industryid=industry_id).all()
            stock_list = [{"stock_id": stock.stockid, "stockname": stock.stockname,
                           "stockprice": stock.stockprice, "industry": stock.industry.industryname}
                          for stock in stocks]

            return {"success": True, "data": stock_list}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_company_name(ts_code):
        """
        根据股票代码获取公司名称
        """
        df = pro.stock_basic(ts_code=ts_code, fields='ts_code,name')
        if not df.empty:
            return df.iloc[0]['name']
        else:
            return None

    @staticmethod
    def get_top10_stocks():
        df = pro.daily(trade_date='20250102')  # 修改为需要的日期

        # 排序：按照涨跌幅 (pct_chg) 排序，降序
        top10 = df.sort_values(by='pct_chg', ascending=False).head(10)

        # 选择股票代码和涨跌幅，转换为适合前端的格式
        top10_data = []
        for _, row in top10.iterrows():
            top10_data.append({
                "name": row['ts_code'],  # 股票代码，或者可以通过额外接口查找公司名称
                "change": row['pct_chg'],  # 涨跌幅
            })

        return top10_data
