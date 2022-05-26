from DbProcess import db_connection

cursor, db = db_connection()

username = "dahai"
sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
cursor.execute(sql_str)
user_id = cursor.fetchall()[0][0]
print(user_id)
