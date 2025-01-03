import tushare as ts


def test_tushare():
    #设置你的token，登录tushare在个人用户中心里拷贝
    ts.set_token('a291eca20fa80c618a74446f824c672e3d9fa2ea4ca0af0199a53410')

    #sina数据
    df = ts.realtime_quote(ts_code='600000.SH,000001.SZ,000001.SH')


    #东财数据
    df = ts.realtime_quote(ts_code='600000.SH', src='dc')

    print(df)


if __name__ == '__main__':
    test_tushare()
