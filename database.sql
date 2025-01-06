CREATE DATABASE stocksystem;

CREATE TABLE user (
    userid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,       -- 用户唯一标识，主键
    username VARCHAR(50) NOT NULL,                        -- 用户名
    password VARCHAR(50) NOT NULL,                        -- 用户密码（加密存储）
    phone NCHAR(13),                                      -- 电话号码
    email VARCHAR(50),                                    -- 邮箱
    address VARCHAR(50),                                  -- 地址
    gender VARCHAR(5),                                    -- 性别
    profession VARCHAR(20),                               -- 职业
    registrationdate DATE NOT NULL,                       -- 用户注册时间
    permissionlevel INT NOT NULL                          -- 用户权限等级
);

CREATE TABLE sentiment (
    sentimentid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,   -- 情感属性唯一标识，主键
    sentiment VARCHAR(255) NOT NULL,                       -- 情感描述，字符串类型
    score DOUBLE NOT NULL                                  -- 预测得分
);

CREATE TABLE source (
    sourceid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,      -- 数据来源唯一标识，主键
    sourcename VARCHAR(50) NOT NULL,                       -- 数据来源名称（如微博等）
    description TEXT                                       -- 数据来源的详细描述
);

CREATE TABLE industry (
    industryid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,   -- 行业唯一标识，主键
    industryname VARCHAR(50) NOT NULL,                     -- 行业名称（如金融、科技等）
    description TEXT                                       -- 行业的详细描述
);

CREATE TABLE stock (
    stockid INT NOT NULL  AUTO_INCREMENT PRIMARY KEY,      -- 股票唯一标识符
    stockcode VARCHAR(20) NOT NULL,                                -- 股票代码
    stockname VARCHAR(100) NOT NULL,                       -- 股票名称
    stockprice FLOAT,                                      -- 股票价格
    industryid INT                                         -- 外键，关联行业表
);

CREATE TABLE selfselect (
    stockid INT NOT NULL,                                  -- 股票唯一标识符
    userid INT NOT NULL,                                    -- 用户ID
    PRIMARY KEY (stockid, userid)                          -- 组合主键，确保每个用户只能选择每只股票一次
);


CREATE TABLE news (
    newsid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,      -- 舆情新闻唯一标识，主键
    title VARCHAR(200) NOT NULL,                          -- 新闻标题
    url VARCHAR(200) NOT NULL ,                   -- 新闻url
    content TEXT NOT NULL,                                -- 新闻内容
    publishdate DATE ,                            -- 新闻发布时间
    sourceid INT ,                                -- 外键，关联数据来源
    industryid INT ,                              -- 外键，关联行业
    sentimentid INT ,                                -- 外键，关联情感属性
    stockid VARCHAR(20)                                 -- 外键，关联股票表
);

CREATE TABLE IF NOT EXISTS news_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            news_id INT,
            sector VARCHAR(255),
            trend VARCHAR(50),
            reason TEXT,
            sentiment VARCHAR(50),
            FOREIGN KEY (id) REFERENCES news(newsid)
)