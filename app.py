from flask import Flask, request, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from DbProcess import *

app = Flask(__name__)

app.secret_key = '123456'

"""login_manager = LoginManager()  # 实例化登录管理对象
login_manager.init_app(app)  # 初始化应用
login_manager.login_view = 'login'  # 设置用户登录视图函数
"""

cursor = db_connection()

cursor.execute("select * from subbank")
bank_data = cursor.fetchall()
bank_list = []
for d in bank_data:
    bank_list.append(d[0])


# 初始页面
@app.route('/')
def index():
    flash("您还没有登录,请先登录或注册")

    return render_template('index.html', bank_list=bank_list)


# 支行详情列表
@app.route('/subbranch/<bank_name>')
def sub_bank(bank_name):
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
                    employee_list.append(temp)
    return render_template('subbranch.html', bank_name=bank_name, employee_list=employee_list)


# 访问注册页面
@app.route('/regist')
def regist():
    return render_template('regist.html')


@app.route('/login_employee')
def login_employee():
    return render_template('login_employee.html')


@app.route('/login_customer')
def login_customer():
    return render_template('login_customer.html')


if __name__ == '__main__':
    app.run(debug=True)
