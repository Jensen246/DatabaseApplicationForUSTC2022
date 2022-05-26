from DbProcess import *

cursor, db = db_connection()

sql_str = "select curdate()"
cursor.execute(sql_str)
date = cursor.fetchall()[0][0]
date = str(date)
print(date)