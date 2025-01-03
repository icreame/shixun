# services/stock_service.py
from model.stock import Stock,db
from model.industry import Industry
from sqlalchemy.sql import text
import tushare as ts
import datetime

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
        """
        获取涨跌幅前10的股票数据
        :param trade_date: 交易日期，默认为'20250102'
        :return: 包含股票代码和涨跌幅的字典列表
        """

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)  # 当前时间减去一天
        trade_time = yesterday.strftime('%Y%m%d')

        df = pro.daily(trade_date=trade_time)  # 获取指定日期的股票数据
        # 排序：按照涨跌幅 (pct_chg) 排序，降序
        top10_up = df.sort_values(by='pct_chg', ascending=False).head(10)
        top10_down = df.sort_values(by='pct_chg', ascending=True).head(10)

        # 选择股票代码和涨跌幅，转换为适合前端的格式
        top10_data = []
        for _, row in top10_up.iterrows():
            try:
                # 获取实时行情，包含股票名称
                realtime_data = ts.realtime_quote(row['ts_code'])  # 单次调用实时行情
                stock_name = realtime_data.loc[0, 'NAME']  # 获取股票名称

                # 添加到返回数据中
                top10_data.append({
                    "name": stock_name,  # 股票名称
                    # "code": row['ts_code'],  # 股票代码
                    "change": row['pct_chg'],  # 涨跌幅
                })
            except Exception as e:
                print(f"Error fetching real-time data for {row['ts_code']}: {e}")
                continue  # 跳过错误的股票

        for _, row in top10_down.iterrows():
            try:
                # 获取实时行情，包含股票名称
                realtime_data = ts.realtime_quote(row['ts_code'])  # 单次调用实时行情
                print(realtime_data)
                print(row['pct_chg'])
                stock_name = realtime_data.loc[0, 'NAME']  # 获取股票名称

                # 添加到返回数据中
                top10_data.append({
                    "name": stock_name,  # 股票名称
                    # "code": row['ts_code'],  # 股票代码
                    "change": row['pct_chg'],  # 涨跌幅
                })
            except Exception as e:
                print(f"Error fetching real-time data for {row['ts_code']}: {e}")
                continue  # 跳过错误的股票
        return top10_data  # 返回最终的前10数据





