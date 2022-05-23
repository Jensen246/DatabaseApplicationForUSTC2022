from flask import Flask, request, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from DbProcess import *

app = Flask(__name__)

app.secret_key = 'PB19030925'

"""login_manager = LoginManager()  # 实例化登录管理对象
login_manager.init_app(app)  # 初始化应用
login_manager.login_view = 'login'  # 设置用户登录视图函数
"""

cursor = db_connection()


# 初始页面
@app.route('/')
def index():
    cursor.execute("select * from subbank")
    data = cursor.fetchall()
    bank_list = []
    for d in data:
        bank_list.append(d[0])
    cursor.execute("select * from department")
    data = cursor.fetchall()
    for d in data:
        for i in range(len(bank_list)):
            if d[1] == bank_list[0]:
                i=1
    flash("您还没有登录,请先登录或注册")

    return render_template('index.html', bank_list=bank_list)

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
