CREATE DATABASE stocksystem;
CREATE TABLE User (
    UserID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,       -- 用户唯一标识，主键
    Username VARCHAR(50) NOT NULL,                        -- 用户名
    Password VARCHAR(50) NOT NULL,                        -- 用户密码（加密存储）
    RegistrationDate DATE NOT NULL,                       -- 用户注册时间
    PermissionLevel INT NOT NULL                          -- 用户权限等级
);
CREATE TABLE Sentiment (
    SentimentID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,  -- 情感属性唯一标识，主键
    SentimentType VARCHAR(20) NOT NULL,                   -- 情感类别（正面、负面、中性）
    Description TEXT                                       -- 情感属性的详细描述
);
CREATE TABLE Source (
    SourceID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,     -- 数据来源唯一标识，主键
    SourceName VARCHAR(50) NOT NULL,                       -- 数据来源名称（如微博等）
    Description TEXT                                       -- 数据来源的详细描述
);
CREATE TABLE Industry (
    IndustryID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,   -- 行业唯一标识，主键
    IndustryName VARCHAR(50) NOT NULL,                     -- 行业名称（如金融、科技等）
    Description TEXT                                       -- 行业的详细描述
);
CREATE TABLE Stock (
    StockID INT NOT NULL PRIMARY KEY,                     -- 股票唯一标识符
    StockName VARCHAR(100) NOT NULL,                        -- 股票名称
    StockPrice FLOAT NOT NULL,                              -- 股票价格
    IndustryID INT NOT NULL,                                -- 外键，关联行业表
    FOREIGN KEY (IndustryID) REFERENCES Industry(IndustryID) -- 外键关联行业表
);
CREATE TABLE SelfSelect (
    StockID INT NOT NULL,                                  -- 股票唯一标识符
    UserID INT NOT NULL,                                    -- 用户ID
    PRIMARY KEY (StockID, UserID),                          -- 组合主键，确保每个用户只能选择每只股票一次
    FOREIGN KEY (StockID) REFERENCES Stock(StockID),        -- 外键关联股票表
    FOREIGN KEY (UserID) REFERENCES User(UserID)           -- 外键关联用户表
);
CREATE TABLE News (
    NewsID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,      -- 舆情新闻唯一标识，主键
    Title VARCHAR(200) NOT NULL,                          -- 新闻标题
    PublishDate DATE NOT NULL,                            -- 新闻发布时间
    Content TEXT NOT NULL,                                -- 新闻内容
    SourceID INT NOT NULL,                                -- 外键，关联数据来源
    IndustryID INT NOT NULL,                              -- 外键，关联行业
    SentimentID INT NOT NULL,                             -- 外键，关联情感属性
    StockID INT NOT NULL,                                -- 外键，关联股票表
    FOREIGN KEY (SourceID) REFERENCES Source(SourceID),  -- 外键关联数据来源表
    FOREIGN KEY (IndustryID) REFERENCES Industry(IndustryID), -- 外键关联行业表
    FOREIGN KEY (SentimentID) REFERENCES Sentiment(SentimentID), -- 外键关联情感属性表
    FOREIGN KEY (StockID) REFERENCES Stock(StockID)      -- 外键关联股票表
);
