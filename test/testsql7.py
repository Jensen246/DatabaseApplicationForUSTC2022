from DbProcess import db_connection

cursor, db = db_connection()

username = "dahai"
sql_str = "select Account_ID from customer inner join customer_checkaccount cc on customer.User_ID = cc.User_ID " \
          "where User_Username = \'" + username + "\'"
cursor.execute(sql_str)
data = cursor.fetchall()
print(data)
