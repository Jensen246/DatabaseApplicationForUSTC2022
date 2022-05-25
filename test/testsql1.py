from DbProcess import *

cursor, db = db_connection()
name = 'jensen'
sql_str = 'select User_Username from customer where User_Username = \'' + name + '\''
cursor.execute(sql_str)
data = cursor.fetchall()
print(data)
print(len(data))
if len(data):
    print(1)
