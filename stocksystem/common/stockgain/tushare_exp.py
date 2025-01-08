import tushare as ts
import json
#设置你的token，登录tushare在个人用户中心里拷贝
ts.set_token('b7378a5c379a258bd7f96c9d3c411d6484b82d0ff3ce312f720abc9c')


def test_tushare():

    #sina数据
    df = ts.realtime_quote(ts_code='600000.SH,000001.SZ,000001.SH')


    #东财数据
    df = ts.realtime_quote(ts_code='600000.SH', src='dc')

    print(df)


def dapan_tushare(ts_code):
    pro = ts.pro_api()

    df = pro.index_basic(ts_code=ts_code)
    print(df)


def dapan_daily(ts_code):
    pro = ts.pro_api()
    df = pro.index_daily(ts_code=ts_code , start_date='20250101', end_date='20250107')
    # 将 DataFrame 转换为 JSON 格式
    json_data = df.to_json(orient='records', force_ascii=False)

    # 返回 JSON 数据
    return json_data


if __name__ == '__main__':
    ts_code = '000001.SH'
    # dapan_tushare(ts_code)
    json_data = dapan_daily(ts_code)
    print(json_data)
