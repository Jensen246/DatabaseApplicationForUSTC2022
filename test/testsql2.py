from DbProcess import *

cursor, db = db_connection()

username = 'dahai'
edit_type = 'User_Name'

sql_str = "select Employee_Password from employee where Employee_Username =" + '\'' + username + '\''
cursor.execute(sql_str)
origin_data = cursor.fetchall()
print(origin_data)
