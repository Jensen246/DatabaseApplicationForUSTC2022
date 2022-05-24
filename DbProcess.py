import MySQLdb

DB_USERNAME = "root"
DB_PASSWORD = "020406"
DB_HOST = "localhost"
DB_NAME = "BankApp"


def db_connection():
    """
    数据库连接
    :return:操作游标
    """
    # 打开数据库连接
    db = MySQLdb.connect(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    return cursor, db
