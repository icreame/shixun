# shixun
实训项目：基于网络舆情的股票分析系统
基于sklearn数据分析

环境：python 3.12

1229：
- 每个模块下面都要有一个 __init__文件，这样其他文件相互引用的时候才不会报错
- 数据库交互用的是SQLALchemy，数据库表没有改
- 前端页面还没有测试过
- 目前只写了用户相关的controller, service, model(文件夹的名称有改动，删去了s)
- 修改所有数据库的字段为小写字段
- 目前可以实现新增用户
- # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+mysqlconnector://shixun:123456@localhost:3306/stocksystem'
    )
  - 这里需要修改成为自己的数据库的用户名和密码

1231：
- 更改了数据库表，使用户表信息更加完善
- 修复了stock表无法自增的问题
- 使用时数据库需要重新建立
- 基本完成了表的基本增删改查逻辑
- 经检验，news表和stock表存在序列化问题，还未解决
- 统一了templates目录下的命名为小写