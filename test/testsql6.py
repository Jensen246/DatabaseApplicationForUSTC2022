from DbProcess import *

cursor, db = db_connection()
username = "dahai"

flag = True
sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
cursor.execute(sql_str)
user_id = cursor.fetchall()[0][0]
print(user_id)

sql_str = "select Account_ID from customer_checkaccount where User_ID = \'" + user_id + "\'"
cursor.execute(sql_str)
flag_data = cursor.fetchall()
print(flag_data)
if len(flag_data):
    flag = False

sql_str = "select Account_ID from customer_depositaccount where User_ID = \'" + user_id + "\'"
cursor.execute(sql_str)
flag_data = cursor.fetchall()
print(flag_data)
if len(flag_data):
    flag = False

sql_str = "select Loan_ID from customer_loan where User_ID = \'" + user_id + "\'"
cursor.execute(sql_str)
flag_data = cursor.fetchall()
print(flag_data)
if len(flag_data):
    flag = False

print(flag)
