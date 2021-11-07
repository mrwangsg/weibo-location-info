-- 用于存储微博打卡，主要信息
CREATE TABLE IF NOT EXISTS weibo_location_info
(
    id                       integer PRIMARY KEY AUTOINCREMENT,
    weibo_mid                varchar(20)  NOT NULL, -- 微博id
    user_info_nick_name      varchar(100) NOT NULL, -- 用户名
    user_info_user_id        varchar(20)  NOT NULL, -- 用户id

    from_info_date           varchar(20)  NOT NULL, -- 微博文，字符串时间
    from_info_timestamp      varchar(20)  NOT NULL, -- 微博文，时间戳
    from_info_url            text,                  -- 微博文，来源地址
    from_info_device         text,                  -- 微博文，来源设备

    content_info_simple_text text,                  --微博正文，脱离html标签，内容
    content_info_html_text   text,                  --微博正文，包含html标签，内容


    data_media_video_id      text,                  --视频id
    data_media_video_tmp_url text,                  --有时效性的视频地址
    data_media_img_list      text,                  --图片集合
    data_media_jump_url      text,                  --跳转链接地址

    status                   integer default 0,     -- 数据状态，用于后期分析数据
    is_delete                integer default 0,     -- 删除状态，0表示未删除，1表示删除
    create_timestamp         varchar(20)  NOT NULL,
    update_timestamp         varchar(20)  NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS index_weibo_location_info_weibo_mid ON weibo_location_info (weibo_mid);


--用于保存微博文对应的打卡地点信息，存在一对多的关系
CREATE TABLE IF NOT EXISTS weibo_location_url_info
(
    id                         integer PRIMARY KEY AUTOINCREMENT,
    weibo_mid                  varchar(20) NOT NULL, -- 微博id(关联使用)
    content_info_location_text text,                 --微博正文，打卡地址(文字)
    content_info_location_url  text,                 --微博正文，打卡地址(链接)
    from_info_date             varchar(20) NOT NULL, -- 微博文，字符串时间
    from_info_timestamp        varchar(20) NOT NULL, -- 微博文，时间戳

    status                     integer default 0,    -- 数据状态，用于后期分析数据
    is_delete                  integer default 0,    -- 删除状态，0表示未删除，1表示删除
    create_timestamp           varchar(20) NOT NULL,
    update_timestamp           varchar(20) NOT NULL
);
CREATE INDEX IF NOT EXISTS index_weibo_location_url_info_weibo_mid ON weibo_location_url_info (weibo_mid);
CREATE INDEX IF NOT EXISTS index_weibo_location_url_info_content_info_location_text ON weibo_location_url_info (content_info_location_text);

