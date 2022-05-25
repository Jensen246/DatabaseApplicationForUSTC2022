from flask import Flask, request, render_template, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from DbProcess import *
from forms_verify import RegisterForm
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

cursor, db = db_connection()

cursor.execute("select Bank_Name from subbank")
bank_data = cursor.fetchall()
bank_list = []
for d in bank_data:
    bank_list.append(d[0])


def return_err_message(template, form):
    """
    将返回错误提示信息功能抽离出来单独作为一个函数
    :param template: html文件
    :param form:
    :return:模板html和错误信息
    """
    print(form.errors)
    err_message = list(form.errors.values())[0][0]  # 错误信息的字符串提取
    print(err_message)
    content = {
        'err_message': err_message
    }
    return render_template(template, **content)


"""
# 一个装饰器功能，但由于
def login_required():
    def decorator(func):
        @wraps(func)  # 保留源信息，本质是endpoint装饰，否则修改函数名很危险
        def inner(*args, **kwargs):  # 接收参数，*args接收多余参数形成元组，**kwargs接收对于参数形成字典
            user = session.get('username')  # 表单接手网页中登录信息，存入到session中，判断用户是否登录
            if not user:
                flash('非法请求')
                return redirect(url_for('index'))  # 没有登录就跳转到未登录的主页
            return func(*args, **kwargs)  # 登录成功就执行传过来的函数
        return inner
    return decorator"""


# 初始页面
@app.route('/')
def index():
    flash("您还没有登录,请先登录或注册")
    return render_template('index.html', bank_list=bank_list)


# 客户登录后的主界面
@app.route('/index_customer/<username>')
def index_customer(username):
    current_user = session.get('username')
    if not current_user or current_user != username:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    return render_template('index_customer.html', bank_list=bank_list)


# 员工登录后主界面，可以看到所有银行的当前资产
@app.route('/index_employee/<username>')
def index_employee(username):
    current_user = session.get('username')
    if not current_user or current_user != username:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    cursor.execute("select Bank_Name,Bank_Property from subbank")
    bank_data_secret = cursor.fetchall()
    bank_list_secret = []
    for line in bank_data_secret:
        bank_list_secret.append([line[0], line[1]])
    return render_template('index_employee.html', bank_list=bank_list_secret)


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
        sql_str = "select Department_ID,Employee_Name,Employee_PhoneNumber,Is_Manager " \
                  "from employee where employee.Department_ID = " + each_depart[0]
        cursor.execute(sql_str)
        employee_data = cursor.fetchall()
        for each_employee in employee_data:
            for i in range(len(department)):
                if department[i][0] == each_employee[0]:
                    # 姓名 部门 电话 身份
                    if each_employee[3]:
                        temp = [each_employee[1], department[i][2], str(each_employee[2]), "经理"]
                    else:
                        temp = [each_employee[1], department[i][2], str(each_employee[2]), "员工"]
                    employee_list.append(temp)
    return render_template('subbranch.html', bank_name=bank_name, employee_list=employee_list)


@app.route('/login_employee', methods=['GET', 'POST'])
def login_employee():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username = username.replace('\'', '\\\'')
        password = password.replace('\'', '\\\'')

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login_employee'))
        sql_str = "select Employee_Password from employee where Employee_Username =" + '\'' + username + '\''
        cursor.execute(sql_str)
        true_password = cursor.fetchall()
        if len(true_password) == 0:
            flash('用户名错误')
            return redirect(url_for('login_employee'))
        if true_password[0][0] == password:
            session['username'] = username
            flash('登录成功，但初始密码很不安全，建议前往个人信息页修改密码')
            return redirect(url_for('index_employee', username=username))
        if check_password_hash(true_password[0][0], password):
            session['username'] = username
            flash('登录成功')
            return redirect(url_for('index_employee'), username=username)
        flash('密码错误')
        return redirect(url_for('login_employee'))
    return render_template('login_employee.html')


@app.route('/login_customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username = username.replace('\'', '\\\'')
        password = password.replace('\'', '\\\'')

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login_employee'))
        sql_str = "select User_Password from customer where user_Username =" + '\'' + username + '\''
        cursor.execute(sql_str)
        true_password = cursor.fetchall()

        if len(true_password) == 0:
            flash('用户名错误')
            return redirect(url_for('login_customer'))
        if true_password[0][0] == password:
            session['username'] = username
            flash('登录成功，但初始密码很不安全，建议前往个人信息页修改密码')
            return redirect(url_for('index_customer', username=username))
        if check_password_hash(true_password[0][0], password):
            session['username'] = username
            flash('登录成功')
            return redirect(url_for('index_customer', username=username))
        flash('密码错误')
        return redirect(url_for('login_customer'))

    return render_template('login_customer.html')


# 访问注册页面，需要检验输入数据的合法性，采用WTforms
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = RegisterForm(request.form)

        if not form.validate():
            flash("输入不合法，注册失败")
            return return_err_message('register.html', form)

        user_id = request.form['user_id']
        user_name = request.form['user_name']
        user_phonenumber = request.form['user_phonenumber']
        user_address = request.form['user_address']
        user_contacts_name = request.form['user_contacts_name']
        user_contacts_phonenumber = request.form['user_contacts_phonenumber']
        user_contacts_email = request.form['user_contacts_email']
        user_contacts_relation = request.form['user_contacts_relation']
        username = request.form['username']
        password = request.form['password']
        password_rep = request.form['password_rep']

        user_name = user_name.replace('\'', '\\\'')
        user_address = user_address.replace('\'', '\\\'')
        user_contacts_name = user_contacts_name.replace('\'', '\\\'')
        username = username.replace('\'', '\\\'')

        sql_str = 'select User_Username from customer where User_Username = \'' + username + '\''
        cursor.execute(sql_str)
        username_verify_1 = cursor.fetchall()
        sql_str = 'select Employee_Username from employee where Employee_Username = \'' + username + '\''
        cursor.execute(sql_str)
        username_verify_2 = cursor.fetchall()
        if len(username_verify_1) or len(username_verify_2):
            flash("用户名已存在，注册失败")
            return redirect(url_for('register'))

        password_hashed = generate_password_hash(password)
        password_hashed = password_hashed.replace('\'', '\\\'')

        sql_str = "insert into customer value (\"" + user_id + "\",\"" + user_name + "\",\"" + user_phonenumber + \
                  "\",\"" + user_address + "\",\"" + user_contacts_name + "\",\"" + user_contacts_phonenumber + \
                  "\",\"" + user_contacts_email + "\",\"" + user_contacts_relation + "\",\"" + username + "\",\"" + \
                  password_hashed + "\")"
        cursor.execute(sql_str)
        db.commit()
        flash("注册成功，自动跳转到登录界面")
        return redirect(url_for('login_customer'))
    return render_template('register.html')


@app.route('/customer_index/<username>')
def customer_index():
    return render_template('customer_index.html')


@app.route('/employee_index/<username>')
def employee_index():
    return render_template('employee_index.html')


# 登出界面
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('登出成功')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
