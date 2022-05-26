from DbProcess import *

cursor, db = db_connection()
username = "dahai"


sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
cursor.execute(sql_str)
user_id = cursor.fetchall()[0][0]

sql_str = "select Account_ID from customer_checkaccount where User_ID = \'" + user_id + "\'"
cursor.execute(sql_str)
flag_data = cursor.fetchall()[0][0]

print(flag_data)
