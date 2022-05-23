from DbProcess import *

cursor = db_connection()

bank_name = "上海总部"

cursor.execute("select * from department")
depart_data = cursor.fetchall()
department = []
for depart in depart_data:
    if depart[1] == bank_name:
        department.append([depart[0], depart[1], depart[2]])  # 部门号 支行名称 部门名称
employee_list = []
for each_depart in department:
    sql_str = "select Department_ID,Employee_Name,Employee_PhoneNumber,Is_Manager from employee where employee.Department_ID = " + \
              each_depart[0]
    cursor.execute(sql_str)
    employee_data = cursor.fetchall()
    for each_employee in employee_data:
        for i in range(len(department)):
            if department[i][0] == each_employee[0]:
                # 姓名 部门 电话 身份
                temp = [each_employee[1], department[i][2], str(each_employee[2]), str(each_employee[3])]
                print(temp)
                employee_list.append(temp)
