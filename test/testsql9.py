from DbProcess import *

cursor, db = db_connection()

sql_str = "select Account_ID from checkaccount"
cursor.execute(sql_str)
account_id_temp_list = cursor.fetchall()
print(account_id_temp_list)
account_id_list = []
for item in account_id_temp_list:
    account_id_list.append(int(item[0][2:]))
print(account_id_list)
new_account_id = "ck" + str(max(account_id_list)+1)
print(new_account_id)
