cd SQL

:: 连接MySQL数据库并执行sql脚本 -f 脚本执行过程中，出现错误继续执行 --default-character-set指定导入数据的编码（与数据库编码相同）
mysql -h localhost -u root --password=020406 bankapp < batch.sql --default-character-set=utf-8

