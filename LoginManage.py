from DbProcess import *
from werkzeug.security import generate_password_hash, check_password_hash


cursor, db = db_connection()


def password_verify(username, password, type_flag):
    """
    密码验证函数
    :param username: 待验证用户名
    :param password: 待验证密码
    :param type_flag: 用户类型，0表示客户，1表示员工
    :return: 0表示用户名错误，1表示登录成功但初始密码不安全，2表示登录成功，4表示密码错误
    """
    if type_flag == 0:
        sql_str = "select User_Password from customer where User_Username =" + '\'' + username + '\''
    if type_flag == 1:
        sql_str = "select Employee_Password from employee where Employee_Username =" + '\'' + username + '\''
    cursor.execute(sql_str)
    true_password = cursor.fetchall()
    if len(true_password) == 0:
        return 0
    if true_password[0][0] == password:
        return 1
    if check_password_hash(true_password[0][0], password):
        return 2
    return 4
