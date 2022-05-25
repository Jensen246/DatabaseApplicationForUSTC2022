from DbProcess import *

cursor, db = db_connection()

username = 'dahai'
sql_str = "select * from customer where User_Username = \'" + username + "\'"
cursor.execute(sql_str)
data = cursor.fetchall()[0]

print(data)
print(len(data))
if len(data):
    print(1)
