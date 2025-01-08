# services/stock_service.py
import logging
import json
import datetime
import random

import numpy as np
from openai import OpenAI
from flask import g, session, jsonify
from collections import OrderedDict
from sqlalchemy.sql import text
from sqlalchemy import or_
import tushare as ts
import akshare as ak
import pandas as pd
import time

from model.index_analysis import IndexAnalysis
from model.index_analysis_result import IndexAnalysisResult
from model.stock import Stock, db
from model.industry import Industry
from flask import g
from flask import session
from collections import OrderedDict
from datetime import datetime, timedelta


# 设置你的 Tushare Token
ts.set_token('b7378a5c379a258bd7f96c9d3c411d6484b82d0ff3ce312f720abc9c')
pro = ts.pro_api()

STOCK_DATA_KEY = "stock_data"
TOP10_DATA="top10_data"

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-10465596f9e847e389a5e22f10c8e58d",  # 替换为你的 API Key
    base_url="https://api.deepseek.com",
)

# 定义系统提示词
system_prompt = """
用户将提供每日的上证指数，深证成指，创业板指数据，科创50数据，请分析各指数的走势，并给出预测、理由以及投资建议。请以json格式输出预测结果。
输入示例：
{
    "参数说明": {
        "ts_code": {
            "类型": "str",
            "描述": "TS指数代码"
        },
        "trade_date": {
            "类型": "str",
            "描述": "交易日"
        },
        "close": {
            "类型": "float",
            "描述": "收盘点位"
        },
        "open": {
            "类型": "float",
            "描述": "开盘点位"
        },
        "high": {
            "类型": "float",
            "描述": "最高点位"
        },
        "low": {
            "类型": "float",
            "描述": "最低点位"
        },
        "pre_close": {
            "类型": "float",
            "描述": "昨日收盘点"
        },
        "change": {
            "类型": "float",
            "描述": "涨跌点"
        },
        "pct_chg": {
            "类型": "float",
            "描述": "涨跌幅（%）"
        },
        "vol": {
            "类型": "float",
            "描述": "成交量（手）"
        },
        "amount": {
            "类型": "float",
            "描述": "成交额（千元）"
        }
    }
}
[{"ts_code":"000001.SH","trade_date":"20250107","close":3229.6439,"open":3203.3068,"high":3230.8529,"low":3190.4612,"pre_close":3206.9228,"change":22.7211,"pct_chg":0.7085,"vol":409660529.0,"amount":436388386.6000000238},{"ts_code":"000001.SH","trade_date":"20250106","close":3206.9228,"open":3209.7832,"high":3219.4877,"low":3185.4631,"pre_close":3211.4299,"change":-4.5071,"pct_chg":-0.1403,"vol":430978403.0,"amount":444188212.8000000119},{"ts_code":"000001.SH","trade_date":"20250103","close":3211.4299,"open":3267.0766,"high":3273.5656,"low":3205.7755,"pre_close":3262.5607,"change":-51.1308,"pct_chg":-1.5672,"vol":517592014.0,"amount":523159754.6999999881},{"ts_code":"000001.SH","trade_date":"20250102","close":3262.5607,"open":3347.9392,"high":3351.722,"low":3242.0865,"pre_close":3351.763,"change":-89.2023,"pct_chg":-2.6614,"vol":561375199.0,"amount":603340526.7000000477}]

输出示例：
{
    "预测": "短期震荡，中性偏乐观",
    "理由": "从提供的数据来看，大盘在20250102日至20250103日经历了较大幅度的下跌，跌幅分别为2.6614%和1.5672%，成交量较高，显示出市场情绪较为悲观。然而，在20250106日，跌幅收窄至0.1403%，且20250107日出现了反弹，涨幅为0.7085%，成交量保持在较高水平，表明市场情绪有所回暖。尽管短期内市场可能仍存在波动，但反弹迹象和成交量的稳定显示出市场可能逐步企稳。因此，预计大盘短期内将呈现震荡走势，但整体情绪偏向中性偏乐观。",
    "情感标签": "中性偏乐观"
    "投资建议": "你的建议"
}
"""

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

            stock_list = []
            for stock in stocks:
                stock_item =  {"stock_id": stock.stockcode,
                "stockname": stock.stockname,
                "stockprice": stock.stockprice}

                if stock.industryid:
                    industry = Industry.query.get(stock.industryid)
                    stock_item["industryname"] = industry.industryname if industry else None

                stock_list.append(stock_item)


            return {"success": True, "data": stock_list}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_stockid_by_stockcode(stockcode):
        """
        根据 stockcode 查询 stockid

        参数:
        stockcode: 股票代码（字符串），用于查询

        返回:
        stockid: 股票ID（字符串），如果未找到则返回 None
        """

        # 假设这里是从数据库中查询的逻辑
        try:
            # 从数据库中查询 stockid
            stock = Stock.query.filter_by(stockcode=stockcode).first()  # 查询与给定stockcode匹配的第一个记录
            if stock is None:  # 检查是否找到股票
                return None  # 如果没有找到，返回 None

            stockid = stock.stockid  # 获取股票ID
            return stockid  # 返回股票ID
        except Exception as e:
            logging.error(f"根据股票代码查询失败, 股票代码: {stockcode}, 错误信息: {str(e)}")  # 记录错误信息
            return None  # 出现错误时返回 None

    @staticmethod
    def search_stocks(query: str, page: int = 1, per_page: int = 10):
        """
        根据查询条件搜索股票，并分页返回结果
        :param query: 搜索关键词
        :param page: 当前页码
        :param per_page: 每页显示数量
        :return: 分页后的股票数据
        """
        try:
            # 基础查询
            query_result = Stock.query

            # 如果有查询关键词，使用数据库的模糊搜索
            if query:
                query_result = query_result.filter(
                    or_(
                        Stock.stockname.ilike(f"%{query}%"),
                        Stock.stockcode.ilike(f"%{query}%")
                    )
                )

                # 分页操作，注意 .items 获取当前页的数据
                paginated_result = query_result.paginate(page=page, per_page=per_page, error_out=False)

                # 构造股票列表
                stock_list = []
                for stock in paginated_result.items:  # 使用 paginated_result.items 获取当前页的数据
                    stock_item = {
                        "stock_id": stock.stockcode,
                        "stockname": stock.stockname,
                    }

                    # 关联行业信息
                    if stock.industryid:
                        industry = Industry.query.get(stock.industryid)
                        stock_item["industry"] = industry.industryname if industry else None

                    stock_list.append(stock_item)

                # 返回分页结果
                return {
                    'data': stock_list,
                    'total': paginated_result.total,
                    'page': paginated_result.page,
                    'per_page': paginated_result.per_page,
                    'total_pages': paginated_result.pages
                }

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
        global  top10_data
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

        top10_data=StockService.get_top10_stocks()

        stock_data = {
            "pe_data": pe_data,
            "ipo_data": ipo_data,
            "sz_count": sz_count,
            "sh_count": sh_count,
            'sh_index': sh_index

        }
        stock_data['last_updated'] = time.time()  # 保存更新时间
        # top10_data['last_updated']= time.time()
        session[STOCK_DATA_KEY] = stock_data
        session[TOP10_DATA]=top10_data

    @staticmethod
    def is_data_expired():
        """检查数据是否过期"""
        if STOCK_DATA_KEY not in session:
            return True  # 如果没有数据，则认为数据过期
        if TOP10_DATA not in session:
            return True  # 如果没有数据，则认为数据过期

        stock_data = session[STOCK_DATA_KEY]
        last_updated = stock_data.get('last_updated', 0)
        current_time = time.time()

        # 判断是否已经过去了一个月（30天）
        if current_time - last_updated > 30 * 24 * 60 * 60:
            return True

        return False

    @staticmethod
    def load_data_from_cache():
        """从 session 加载数据"""
        return session.get(STOCK_DATA_KEY, None)

    @staticmethod
    def loadtop10_data_from_cache():
        """从 session 加载数据"""
        return session.get(TOP10_DATA, None)

    def set_data_in_cache(stock_data, top10_data):
        """将数据存储到 session"""
        session[STOCK_DATA_KEY] = stock_data
        session[STOCK_DATA_KEY] = top10_data

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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_index_data():
        # 获取上证指数数据
        sh_index = pro.index_daily(ts_code='000001.SH')
        # 获取深证成指数据
        sz_index = pro.index_daily(ts_code='399001.SZ')
        # 获取创业板指数据
        cyb_index = pro.index_daily(ts_code='399006.SZ')
        # 获取科创50数据
        kc50_index = pro.index_daily(ts_code='000688.SH')

        # 返回 JSON 数据
        return {
            'sh_index': sh_index.to_dict(orient='records'),
            'sz_index': sz_index.to_dict(orient='records'),
            'cyb_index': cyb_index.to_dict(orient='records'),
            'kc50_index': kc50_index.to_dict(orient='records')
        }

    @staticmethod
    def get_limit_stocks():
        """
        获取昨日A股的涨跌数据
        :return: 返回涨停和跌停股票的DataFrame
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)  # 当前时间减去一天
        trade_time = yesterday.strftime('%Y%m%d')

        df = pro.daily(trade_date=trade_time)  # 获取指定日期的股票数据
        pct_chg = df['pct_chg']

        # 存储昨日收盘价
        close = df['close']
        for idx, price in close.items():
            stock = Stock.query.get(idx + 1)  # 获取id为idx+1的股票
            if stock:  # 确保找到了对应的股票
                stock.stockprice = price
                db.session.commit()

        # 定义区间边界
        bins = [-float('inf'), -8, -6, -4, -2, 0, 2, 4, 6, 8, float('inf')]
        labels = ['<-8%', '<-6%', '<-4%', '<-2%', '<0%', '<2%', '<4%', '<6%', '<8%', '>8%']

        # 使用pd.cut将涨跌幅划分到指定的区间
        pct_chg_bins = pd.cut(pct_chg, bins=bins, labels=labels)

        # 统计每个区间的股票数量
        counts = pct_chg_bins.value_counts().sort_index()

        # 将 int64 转换为 Python 原生 int
        counts = counts.astype(int)

        # 上涨股票数量
        up_count = len(df[df['pct_chg'] > 0])
        # 下跌股票数量
        down_count = len(df[df['pct_chg'] < 0])

        # 将统计结果按顺序排列并返回为列表
        result = [int(counts.get(label, 0)) for label in labels]  # 确保每个值都是 Python 原生 int

        # 使用 OrderedDict 保持顺序（【0107】不然因为json是无序的，所以输出也是无序的，好像没用？）
        results = OrderedDict([
            ("up_total", int(up_count)),
            ("down_total", int(down_count)),
            ("data", result)
        ])

        return results

    @staticmethod
    def get_stock_limit_data():
        # 初始化时间范围和股票数据
        time_range = []  # 时间范围
        up_limit = []  # 涨停股票数量
        down_limit = []  # 跌停股票数量

        # 设置起始时间和结束时间
        start_time = datetime.strptime("09:30", "%H:%M")  # 开始时间改为 09:30
        end_time = datetime.strptime("14:56", "%H:%M")  # 结束时间改为 14:56

        # 计算总分钟数
        total_minutes = int((end_time - start_time).total_seconds() / 60)

        # 生成基础趋势线（线性增长或下降）
        base_up_trend = np.linspace(20, 70, total_minutes)  # 涨停数量从 20 逐渐增加到 70
        base_down_trend = np.linspace(60, 10, total_minutes)  # 跌停数量从 60 逐渐减少到 10

        # 生成每分钟的数据
        current_time = start_time
        for i in range(total_minutes):
            # 格式化时间为 HH:MM
            time_range.append(current_time.strftime("%H:%M"))

            # 在基础趋势线上添加随机波动（使用高斯分布）
            up = int(base_up_trend[i] + random.gauss(0, 3))  # 均值为 0，标准差为 3
            down = int(base_down_trend[i] + random.gauss(0, 3))  # 均值为 0，标准差为 3

            # 确保涨停和跌停数量在 0 到 80 之间
            up = max(0, min(up, 80))
            down = max(0, min(down, 80))

            # 添加到结果中
            up_limit.append(up)
            down_limit.append(down)

            # 增加一分钟
            current_time += timedelta(minutes=1)

        # 返回生成的数据
        return {
            "time_range": time_range,
            "up_limit": up_limit,
            "down_limit": down_limit
        }

    @staticmethod
    def fetch_and_store_index_data():
        """
        获取当前一周的指数详情并存入数据库。
        """
        # 获取当前日期
        end_date = datetime.datetime.now().strftime('%Y%m%d')
        # 计算一周前的日期
        start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y%m%d')

        # 获取上证指数数据
        sh_index = pro.index_daily(ts_code='000001.SH', start_date=start_date, end_date=end_date)
        # 获取深证成指数据
        sz_index = pro.index_daily(ts_code='399001.SZ', start_date=start_date, end_date=end_date)
        # 获取创业板指数据
        cyb_index = pro.index_daily(ts_code='399006.SZ', start_date=start_date, end_date=end_date)
        # 获取科创50数据
        kc50_index = pro.index_daily(ts_code='000688.SH', start_date=start_date, end_date=end_date)

        # 按日期排序（最新的日期在前）
        sh_index = sh_index.sort_values(by='trade_date', ascending=False)
        sz_index = sz_index.sort_values(by='trade_date', ascending=False)
        cyb_index = cyb_index.sort_values(by='trade_date', ascending=False)
        kc50_index = kc50_index.sort_values(by='trade_date', ascending=False)

        # 将数据转换为 JSON 格式
        json_data = {
            'sh_index': sh_index.to_dict(orient='records'),
            'sz_index': sz_index.to_dict(orient='records'),
            'cyb_index': cyb_index.to_dict(orient='records'),
            'kc50_index': kc50_index.to_dict(orient='records')
        }

        # 将数据存入数据库
        try:
            new_analysis = IndexAnalysis(
                analysis_date=datetime.datetime.now().date(),
                sh_index=json.dumps(json_data['sh_index']),
                sz_index=json.dumps(json_data['sz_index']),
                cyb_index=json.dumps(json_data['cyb_index']),
                kc50_index=json.dumps(json_data['kc50_index'])
            )
            db.session.add(new_analysis)
            db.session.commit()
            return json_data
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_index_data_from_db():
        """
        从数据库中读取本周的指数详情，如果没有则调用 fetch_and_store_index_data 函数获取数据并存入数据库。
        """
        # 获取当前日期
        end_date = datetime.datetime.now().date()
        # 计算一周前的日期
        start_date = end_date - datetime.timedelta(days=7)

        # 查询本周的数据
        try:
            analysis_data = IndexAnalysis.query.filter(
                IndexAnalysis.analysis_date >= start_date,
                IndexAnalysis.analysis_date <= end_date
            ).first()

            # 如果数据库中没有本周的数据，则调用 fetch_and_store_index_data 函数获取数据并存入数据库
            if not analysis_data:
                return StockService.fetch_and_store_index_data()
            else:
                return {
                    'sh_index': json.loads(analysis_data.sh_index),
                    'sz_index': json.loads(analysis_data.sz_index),
                    'cyb_index': json.loads(analysis_data.cyb_index),
                    'kc50_index': json.loads(analysis_data.kc50_index)
                }
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def composite_index_analysis():
        """
        获取最近一周的大盘数据，并将其整理为 JSON 格式，传递给大模型进行分析。
        将大模型的分析结果存入数据库。

        :return: JSON 对象，包含四个指数的最近一周分析结果
        """
        # 获取当前日期
        end_date = datetime.datetime.now().date()
        # 计算一周前的日期
        start_date = end_date - datetime.timedelta(days=7)

        # 检查数据库中是否已经有本周的分析结果
        try:
            analysis_result = IndexAnalysisResult.query.filter(
                IndexAnalysisResult.analysis_date >= start_date,
                IndexAnalysisResult.analysis_date <= end_date
            ).first()

            # 如果数据库中没有本周的分析结果，则调用大模型获取并存储
            if not analysis_result:
                # 获取本周的指数数据
                json_data = StockService.get_index_data_from_db()

                # 用户提示词，传入大盘数据
                user_prompt = f"请分析我给你的大盘数据，用json格式给出输出，大盘数据如下：{json_data}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

                # 调用大模型
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    response_format={'type': 'json_object'}  # 指定返回 JSON 格式
                )

                # 解析大模型返回的结果
                analysis_result = json.loads(response.choices[0].message.content)
                print("Analysis result from model:", analysis_result)  # 打印分析结果

                # 提取并组合 cyb_index 相关的数据
                cyb_index_data = {
                    "情感标签": analysis_result["情感标签"]["cyb_index"],
                    "投资建议": analysis_result["投资建议"]["cyb_index"],
                    "理由": analysis_result["理由"]["cyb_index"],
                    "预测": analysis_result["预测"]["cyb_index"]
                }

                # 提取并组合 kc50_index 相关的数据
                kc50_index_data = {
                    "情感标签": analysis_result["情感标签"]["kc50_index"],
                    "投资建议": analysis_result["投资建议"]["kc50_index"],
                    "理由": analysis_result["理由"]["kc50_index"],
                    "预测": analysis_result["预测"]["kc50_index"]
                }

                # 提取并组合 sh_index 相关的数据
                sh_index_data = {
                    "情感标签": analysis_result["情感标签"]["sh_index"],
                    "投资建议": analysis_result["投资建议"]["sh_index"],
                    "理由": analysis_result["理由"]["sh_index"],
                    "预测": analysis_result["预测"]["sh_index"]
                }

                # 提取并组合 sz_index 相关的数据
                sz_index_data = {
                    "情感标签": analysis_result["情感标签"]["sz_index"],
                    "投资建议": analysis_result["投资建议"]["sz_index"],
                    "理由": analysis_result["理由"]["sz_index"],
                    "预测": analysis_result["预测"]["sz_index"]
                }

                # 将分析结果存入数据库
                new_analysis = IndexAnalysisResult(
                    analysis_date=datetime.datetime.now().date(),
                    cyb_index_analysis=json.dumps(cyb_index_data),
                    kc50_index_analysis=json.dumps(kc50_index_data),
                    sh_index_analysis=json.dumps(sh_index_data),
                    sz_index_analysis=json.dumps(sz_index_data)
                )
                print("New analysis object:", new_analysis)  # 打印新对象

                db.session.add(new_analysis)
                print("Data added to session")  # 打印日志
                db.session.commit()
                print("Data committed to database")  # 打印日志

                return analysis_result
            else:
                # 如果数据库中有本周的分析结果，则直接返回
                return {
                    'cyb_index': json.loads(analysis_result.cyb_index_analysis),
                    'kc50_index': json.loads(analysis_result.kc50_index_analysis),
                    'sh_index': json.loads(analysis_result.sh_index_analysis),
                    'sz_index': json.loads(analysis_result.sz_index_analysis)
                }
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to database: {e}")  # 打印错误信息
            return {"success": False, "message": str(e)}