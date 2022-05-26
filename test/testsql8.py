from DbProcess import *

cursor, db = db_connection()

option_bank = "上海总部"
sql_str = "select Employee_ID,Employee_Name,Is_Manager from employee " \
                  "inner join department d on employee.Department_ID = d.Department_ID " \
                  "inner join subbank s on d.Bank_Name = s.Bank_Name " \
                  "where d.Department_Name =\'客服部\' and d.Bank_Name = \'"+ option_bank + "\'"
cursor.execute(sql_str)
data = cursor.fetchall()
print(data)
