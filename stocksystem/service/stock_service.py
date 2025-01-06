# services/stock_service.py
from model.stock import Stock,db
from model.industry import Industry
from sqlalchemy.sql import text
import tushare as ts
import datetime
import akshare as ak
import pandas as pd
import time
from flask import g
from flask import session

# 设置你的 Tushare Token
ts.set_token('b7378a5c379a258bd7f96c9d3c411d6484b82d0ff3ce312f720abc9c')
pro = ts.pro_api()

STOCK_DATA_KEY = "stock_data"
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
            return {"id":new_stock.stockid,"stockname":stockname,"stockprice":stockprice,"industry":new_stock.industry.industryname}
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
    def update_data():
        global stock_data
        # 获取pe
        pe_data = StockService.get_pe_data()

        # 获取 IPO 数据
        ipo_data = StockService.get_ipo_data()

        # 上市公司数量
        market = StockService.get_stock_counts()
        sz_count = market['sz_count']
        sh_count = market['sh_count']

        # 上证指数
        sh_index = StockService.get_sh_index_data()

        stock_data = {
            "pe_data": pe_data,
            "ipo_data": ipo_data,
            "sz_count": sz_count,
            "sh_count": sh_count,
            'sh_index': sh_index

        }
        stock_data['last_updated'] = time.time()  # 保存更新时间
        session[STOCK_DATA_KEY] = stock_data
        print("update")

    @staticmethod
    def is_data_expired():
        """检查数据是否过期"""
        if STOCK_DATA_KEY not in session:
            return True  # 如果没有数据，则认为数据过期

        stock_data = session[STOCK_DATA_KEY]
        last_updated = stock_data.get('last_updated', 0)
        current_time = time.time()

        # 判断是否已经过去了一个月（30天）
        if current_time - last_updated > 30 * 24 * 60 * 60:
            return True

        return False

    def load_data_from_cache():
        """从 session 加载数据"""
        return session.get(STOCK_DATA_KEY, None)

    def set_data_in_cache(stock_data):
        """将数据存储到 session"""
        session[STOCK_DATA_KEY] = stock_data

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

    # 获取A股上市公司数量（深市和沪市）
    def get_stock_counts():
        try:
            # 获取所有A股上市公司的基本信息
            stock_basic = pro.stock_basic(list_status='L', exchange='', fields='ts_code,exchange')
            print("stock")
            print(stock_basic)
            # 统计深市和沪市上市公司的数量
            sz_count = stock_basic[stock_basic['exchange'] == 'SZSE'].shape[0]  # 深市
            sh_count = stock_basic[stock_basic['exchange'] == 'SSE'].shape[0]  # 沪市
            result={
                'sz_count': sz_count, 'sh_count': sh_count
            }
            print("shangshi")
            print(result)
            # 返回结果
            return result

        except Exception as e:
            print(f"获取A股上市公司数据时出错：{e}")
            return None

    # 获取PE对比数据
    def get_pe_data():
        try:
        # 获取四个指数的日线数据
            indices = ['000001.SH', '399001.SZ', '399005.SZ', '399006.SZ']  # 上证、深证、中小板、创业板
            index_data = {}

            for index in indices:
                df = pro.index_daily(ts_code=index, start_date='20180101', end_date='20231231')
                df['trade_date'] = pd.to_datetime(df['trade_date'])  # 将日期列转换为日期格式
                df.set_index('trade_date', inplace=True)

                # 按季度汇总数据（取季度末的收盘价作为该季度的代表指数）
                quarterly_data = df['close'].resample('Q').last()  # 取每季度最后一天的收盘价
                index_data[index] = quarterly_data

            # 将四个指数数据合并为一个 DataFrame
            all_index_data = pd.DataFrame(index_data)

            # 获取季度
            all_index_data['quarter'] = all_index_data.index.strftime('%Y-Q%q')
            sh1 = all_index_data['000001.SH'].tolist()
            sz1= all_index_data['399001.SZ'].tolist()
            sz5 = all_index_data['399005.SZ'].tolist()
            sz6 = all_index_data['399006.SZ'].tolist()
            result = {
                'sh1': sh1,
                'sz1': sz1,
                'sz5': sz5,
                'sz6': sz6
            }
            print("sh1")
            print(result)
            # return all_index_data[['quarter', '000001.SH', '399001.SZ', '399005.SZ', '399006.SZ']]
            return result
        except Exception as e:
            print(f"获取pe数据时出错：{e}")  # 捕获异常并打印错误信息
            return None  #

    # 获取IPO数据
    def get_ipo_data():
        try:
            ipo_data = pro.new_share(start_date='20180101', end_date='20240101')  # 获取近五年的IPO数据

            ipo_data['issue_date'] = pd.to_datetime(ipo_data['issue_date'])  # 将日期列转换为日期类型
            # 提取季度
            ipo_data['quarter'] = ipo_data['issue_date'].dt.to_period('Q')

            # 按季度分组，计算每个季度的IPO数量和募集资金总额
            annual_data = ipo_data.groupby('quarter').agg(
                ipo_count=('amount', 'size'),  # 每个季度的IPO数量
                issue_count=('amount', 'sum')  # 每个季度的募集资金总额
            ).reset_index()

            # 将季度转换为字符串格式（如 '2018Q1', '2018Q2' 等）
            annual_data['quarter'] = annual_data['quarter'].astype(str)

            # 提取年份、IPO数量、募集资金
            quarters = annual_data['quarter'].tolist()  # 获取年份列表
            ipo_count = annual_data['ipo_count'].tolist()  # 获取IPO数量列表
            # issue_count = annual_data['issue_count'].tolist()  # 获取募集资金列表

            # 将数据构建为字典格式
            result = {
                'dates': quarters,
                'ipo_count': ipo_count,  # 存储IPO数量
                # 'issue_count': issue_count  # 存储募集资金
            }
            return result  # 返回字典
        except Exception as e:
            print(f"获取IPO数据时出错：{e}")  # 捕获异常并打印错误信息
            return None  # 返回None以表示出错

    def get_sh_index_data():
        try:

            sh_index_data = pro.index_daily(ts_code='000001.SH', start_date='20180101', end_date='20231231')  # 获取上证指数数据

            # 将日期列转换为日期格式
            sh_index_data['trade_date'] = pd.to_datetime(sh_index_data['trade_date'])

            # 提取季度信息
            sh_index_data['quarter'] = sh_index_data['trade_date'].dt.to_period('Q')

            # 按季度分组，计算每个季度的平均上证指数
            quarterly_index = sh_index_data.groupby('quarter').agg(
                avg_index=('close', 'mean')  # 每个季度的平均上证指数
            ).reset_index()

            # 转换季度为字符串格式（如 '2018Q1', '2018Q2' 等）
            quarterly_index['quarter'] = quarterly_index['quarter'].astype(str)

            # 获取每个季度的平均指数并放入列表
            result = quarterly_index['avg_index'].tolist()
            result = {
                'values': result
            }
            return result  # 返回每个季度的上证指数数据
        except Exception as e:
            print(f"获取上证指数数据时出错：{e}")
            return None  # 返回None以表示出错

