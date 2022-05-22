import MySQLdb

DB_USERNAME = "root"
DB_PASSWORD = "020406"
DB_HOST = "localhost"
DB_NAME = "BankApp"


def Execute_File(sql_file, foreign_check):
    """
    运行sql文件
    :param sql_file: 待执行的sql文件路径
    :param foreign_check: 外键检查开关，1表示打开，0表示关闭
    :return: 无
    """
    try:
        # 打开数据库连接
        db = MySQLdb.connect(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)

        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        if not foreign_check:
            cursor.execute("SET foreign_key_checks = 0;")
        with open(sql_file, encoding='utf-8', mode='r') as f:
            # 读取整个sql文件，以分号切割。[:-1]删除最后一个元素，也就是空字符串
            sql_list = f.read().split(';')[:-1]
            for x in sql_list:
                # 判断包含空行的
                if '\n' in x:
                    # 替换空行为1个空格
                    x = x.replace('\n', ' ')

                    """# 判断多个空格时
                    if '    ' in x:
                        # 替换为空
                        x = x.replace('    ', '')"""

                    # sql语句添加分号结尾
                    sql_item = x + ';'
                    # print(sql_item)
                    cursor.execute(sql_item)
                    print("执行成功sql: %s" % sql_item)
    except Exception as e:
        print(e)
        print('执行失败sql: %s' % sql_item)
    finally:
        # 关闭mysql连接
        if not foreign_check:
            cursor.execute("SET foreign_key_checks = 1;")
        result = cursor.fetchall()
        for data in result:
            print(data)
        db.close()


def Execute_Sentence(sql_sentence):
    """
    运行sql语句并返回结果
    :param sql_sentence: sql语句
    :return: 无
    """
    # 打开数据库连接
    db = MySQLdb.connect(DB_HOST, DB_USERNAME, DB_PASSWORD)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    cursor.execute(sql_sentence)

    result = cursor.fetchall()
    for data in result:
        print(data)
    db.close()
