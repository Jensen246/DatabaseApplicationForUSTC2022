from DbProcess import *
from werkzeug.security import check_password_hash

cursor, db = db_connection()

username = 'dahai'
sql_str = "select User_Password from customer where User_Username =" + '\'' + username + '\''
cursor.execute(sql_str)
true_password = cursor.fetchall()[0][0]
print(len(true_password))
print(true_password)

flag1 = check_password_hash(true_password, '123456')
print(flag1)
flag2 = check_password_hash(true_password, '1234567')
print(flag2)
flag3 = check_password_hash(true_password, '12345678')
print(flag3)
flag3 = check_password_hash(true_password, 'qwertyu')
print(flag3)
