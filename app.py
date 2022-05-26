from flask import Flask, request, render_template, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
# from LoginManage import *
from DbProcess import *
from forms_verify import *
from functools import wraps
import copy

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

cursor, db = db_connection()

cursor.execute("select Bank_Name from subbank")
bank_data = cursor.fetchall()
bank_list = []
for d in bank_data:
    bank_list.append(d[0])

cursor.execute("select curdate()")
date = cursor.fetchall()[0][0]
date = str(date)


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
    # flash(bank_list)
    flash("您还没有登录,请先登录或注册")
    return render_template('index.html', bank_list=bank_list)


# 客户登录后的主界面
@app.route('/index_customer/<username>')
def index_customer(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    return render_template('index_customer.html', bank_list=bank_list, username=username)


# 员工登录后主界面，可以看到所有银行的当前资产
@app.route('/index_employee/<username>')
def index_employee(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    cursor.execute("select Bank_Name,Bank_Property from subbank")
    bank_data_secret = cursor.fetchall()
    bank_list_secret = []
    for line in bank_data_secret:
        bank_list_secret.append([line[0], line[1]])
    return render_template('index_employee.html', bank_list=bank_list_secret, username=username)


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
            flash('用户名或密码不能为空，请重新输入')
            return redirect(url_for('login_employee'))
        sql_str = "select Employee_Password from employee where Employee_Username =" + '\'' + username + '\''
        cursor.execute(sql_str)
        true_password = cursor.fetchall()
        if len(true_password) == 0:
            flash('用户名错误')
            return redirect(url_for('login_employee'))
        if true_password[0][0] == password:
            session[username] = True
            flash('登录成功，但初始密码很不安全，建议前往个人信息页修改密码')
            return redirect(url_for('index_employee', username=username))
        if check_password_hash(true_password[0][0], password):
            session[username] = True
            flash('登录成功')
            return redirect(url_for('index_employee', username=username))
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
            flash('用户名或密码不能为空，请重新输入')
            return redirect(url_for('login_employee'))
        sql_str = "select User_Password from customer where user_Username =" + '\'' + username + '\''
        cursor.execute(sql_str)
        true_password = cursor.fetchall()

        if len(true_password) == 0:
            flash('用户名错误')
            return redirect(url_for('login_customer'))
        if true_password[0][0] == password:
            session[username] = True
            flash('登录成功，但初始密码很不安全，建议前往个人信息页修改密码')
            return redirect(url_for('index_customer', username=username))
        if check_password_hash(true_password[0][0], password):
            session[username] = True
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


# 登出界面
@app.route('/logout/<username>')
def logout(username):
    session.pop(username)
    flash('登出成功')
    return redirect(url_for('index'))


@app.route('/customer_index/<username>')
def customer_index(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    return render_template('customer_index.html', methods=['GET', 'POST'])


@app.route('/employee_index/<username>')
def employee_index(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    return render_template('employee_index.html')


@app.route('/info_customer/<username>')
def info_customer(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select * from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    customer_data = cursor.fetchall()[0]
    return render_template('info_customer.html', customer_data=customer_data, username=username)


@app.route('/info_employee/<username>')
def info_employee(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select * from employee where Employee_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    employee_data = cursor.fetchall()[0]
    employee_data = list(employee_data)
    if employee_data[8]:
        employee_data[8] = '经理'
    else:
        employee_data[8] = '普通员工'
    sql_str = "select * from department"
    cursor.execute(sql_str)
    department_data = cursor.fetchall()
    for department in department_data:
        if department[0] == employee_data[1]:
            temp = department
    return render_template('info_employee.html', employee_data=employee_data, username=username, department=temp)


@app.route('/edit_customer_info/<username>/<edit_type>', methods=['GET', 'POST'])
def edit_customer_info(username, edit_type):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select * from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    customer_data = cursor.fetchall()[0]

    if request.method == 'POST':
        changed_data = request.form['changed_data']
        if not verify_edit(simple_type[edit_type], changed_data):
            flash("输入不符合格式要求！")
            return redirect(url_for('edit_customer_info', username=username, edit_type=edit_type))
        changed_data = changed_data.replace('\'', '\\\'')
        sql_str = "update customer set " + edit_type + " = \'" + changed_data + "\'" + \
                  "where User_Username = \'" + username + "\'"
        cursor.execute(sql_str)
        db.commit()
        flash("修改成功，跳转回个人信息页")

        sql_str = "select * from customer where User_Username = \'" + username + "\'"
        cursor.execute(sql_str)
        customer_data = cursor.fetchall()[0]
        return redirect(url_for('info_customer', username=username))
    return render_template('edit_customer_info.html',
                           username=username, edit_type=edit_type, customer_data=customer_data)


@app.route('/edit_customer_password/<username>', methods=['GET', 'POST'])
def edit_customer_password(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        rep_password = request.form['rep_password']

        sql_str = "select User_Password from customer where User_Username =" + '\'' + username + '\''
        cursor.execute(sql_str)
        true_password = cursor.fetchall()
        if not true_password[0][0] == old_password:
            if not check_password_hash(true_password[0][0], old_password):
                flash('旧密码不正确')
                return redirect(url_for('edit_customer_password', username=username))
        if not 5 <= len(new_password) <= 12:
            flash('新密码格式不符合要求')
            return redirect(url_for('edit_customer_password', username=username))
        if new_password != rep_password:
            flash('两次输入的新密码不一致')
            return redirect(url_for('edit_customer_password', username=username))
        new_password_hashed = generate_password_hash(new_password)
        new_password_hashed = new_password_hashed.replace('\'', '\\\'')
        sql_str = "update customer set User_Password = \'" + new_password_hashed + "\'" + \
                  "where User_Username = \'" + username + "\'"
        cursor.execute(sql_str)
        db.commit()

        flash("修改成功，跳转到登录界面")
        session.pop(username)
        return redirect(url_for('login_customer'))
    return render_template('edit_customer_password.html', username=username)


@app.route('/edit_employee_password/<username>', methods=['GET', 'POST'])
def edit_employee_password(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        rep_password = request.form['rep_password']

        sql_str = "select Employee_Password from employee where Employee_Username =" + '\'' + username + '\''
        cursor.execute(sql_str)
        true_password = cursor.fetchall()
        if not true_password[0][0] == old_password:
            if not check_password_hash(true_password[0][0], old_password):
                flash('旧密码不正确')
                return redirect(url_for('edit_employee_password', username=username))
        if not 5 <= len(new_password) <= 12:
            flash('新密码格式不符合要求')
            return redirect(url_for('edit_employee_password', username=username))
        if new_password != rep_password:
            flash('两次输入的新密码不一致')
            return redirect(url_for('edit_employee_password', username=username))
        new_password_hashed = generate_password_hash(new_password)
        new_password_hashed = new_password_hashed.replace('\'', '\\\'')
        sql_str = "update employee set Employee_Password = \'" + new_password_hashed + "\'" + \
                  "where Employee_Username = \'" + username + "\'"
        cursor.execute(sql_str)
        db.commit()

        flash("修改成功，跳转到登录界面")
        session.pop(username)
        return redirect(url_for('login_employee'))
    return render_template('edit_employee_password.html', username=username)


@app.route('/delete_customer/<username>')
def delete_customer(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    flag = True
    sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    user_id = cursor.fetchall()[0][0]

    sql_str = "select Account_ID from customer_checkaccount where User_ID = \'" + user_id + "\'"
    cursor.execute(sql_str)
    flag_data = cursor.fetchall()
    if len(flag_data):
        flag = False

    sql_str = "select Account_ID from customer_depositaccount where User_ID = \'" + user_id + "\'"
    cursor.execute(sql_str)
    flag_data = cursor.fetchall()
    if len(flag_data):
        flag = False

    sql_str = "select Loan_ID from customer_loan where User_ID = \'" + user_id + "\'"
    cursor.execute(sql_str)
    flag_data = cursor.fetchall()
    if len(flag_data):
        flag = False

    if not flag:
        flash("不满足注销用户条件：存在关联账户或贷款记录")
        return redirect(url_for('info_customer', username=username))

    sql_str = "delete from customer where User_ID = \'" + user_id + "\'"
    cursor.execute(sql_str)
    db.commit()
    flash("注销成功，跳转到主界面")
    session.pop(username)
    return redirect(url_for('index'))


@app.route('/check_account_customer/<username>')
def check_account_customer(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    have_check_account = False

    sql_str = "select Account_ID from customer inner join customer_checkaccount cc on customer.User_ID = cc.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_id_list = cursor.fetchall()
    check_account_id_list = []
    for temp_id in temp_id_list:
        check_account_id_list.append(temp_id[0])

    check_account_data = []
    if len(check_account_id_list):
        have_check_account = True
        for check_account_id in check_account_id_list:
            sql_str = "select * from checkaccount where Account_ID = \'" + check_account_id + "\'"
            cursor.execute(sql_str)
            check_account_data.append(cursor.fetchall()[0])
        # flash(check_account_data)
        return render_template('check_account_customer.html', username=username,
                               have_check_account=have_check_account, check_account_data=check_account_data)
    else:
        return render_template('check_account_customer.html', username=username,
                               have_check_account=have_check_account, check_account_data=check_account_data)


@app.route('/open_check_account/<username>', methods=['GET', 'POST'])
def open_check_account(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    sql_str = "select Bank_Name from customer inner join customer_checkaccount cc on customer.User_ID = cc.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_bank_list = cursor.fetchall()
    open_bank_list = []
    for temp_bank in temp_bank_list:
        open_bank_list.append(temp_bank[0])

    if len(open_bank_list) == len(bank_list):
        flash("您已经在所有支行都注册了支票账户，无法再注册新账户")
        return redirect(url_for('check_account_customer', username=username))

    option_bank_list = copy.deepcopy(bank_list)  # python中直接用等号不是拷贝而是等价
    for item in open_bank_list:
        option_bank_list.remove(item)

    employee_dict = {}
    for option_bank in option_bank_list:
        employee_dict[option_bank] = []
        sql_str = "select Employee_Name,Employee_PhoneNumber,Is_Manager from employee " \
                  "inner join department d on employee.Department_ID = d.Department_ID " \
                  "inner join subbank s on d.Bank_Name = s.Bank_Name " \
                  "where d.Department_Name =\'客服部\' and d.Bank_Name = \'" + option_bank + "\'"
        cursor.execute(sql_str)
        option_employee_list = cursor.fetchall()
        for option_employee in option_employee_list:
            option_employee = list(option_employee)
            if option_employee[2] == 1:
                option_employee[2] = "经理"
            else:
                option_employee[2] = "员工"
            employee_dict[option_bank].append(option_employee)

    return render_template('open_check_account.html', username=username,
                           option_bank_list=option_bank_list, employee_dict=employee_dict, bank_list=bank_list)


@app.route('/build_check_account/<username>_<employee>_<bank>')
def build_check_account(username, employee, bank):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    user_id = cursor.fetchall()[0][0]

    sql_str = "select Employee_ID from employee where Employee_Name = \'" + employee + "\'"
    cursor.execute(sql_str)
    employee_id = cursor.fetchall()[0][0]

    sql_str = "select Account_ID from checkaccount"
    cursor.execute(sql_str)
    account_id_temp_list = cursor.fetchall()
    account_id_list = []
    # 获取ck后的数字位
    for item in account_id_temp_list:
        account_id_list.append(int(item[0][2:]))
    new_account_id = "ck" + str(max(account_id_list) + 1)

    sql_str = "insert into checkaccount " \
              "value (\'" + new_account_id + "\', 0, \'" + date + "\',\'" + bank + "\', 20000)"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "insert into customer_checkaccount " \
              "value (\'" + user_id + "\',\'" + bank + "\',\'" + new_account_id + "\',\'" + date + "\')"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "insert into employee_customer value (\'" + employee_id + "\',\'" + user_id + "\',\'ck\')"
    cursor.execute(sql_str)
    db.commit()

    flash("支票账户开户成功，跳转支票账户界面")
    return redirect(url_for('check_account_customer', username=username))


@app.route('/delete_check_account/<username>_<check_account_id>_')
def delete_check_account(username, check_account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    user_id = cursor.fetchall()[0][0]

    sql_str = "select Account_balance,Reg_Bank from checkaccount where Account_ID = \'" + check_account_id + "\'"
    cursor.execute(sql_str)
    balance, bank = cursor.fetchall()[0]

    sql_str = "select Employee_ID from employee " \
              "inner join department d on employee.Department_ID = d.Department_ID " \
              "inner join subbank s on d.Bank_Name = s.Bank_Name " \
              "inner join customer_checkaccount cc on s.Bank_Name = cc.Bank_Name " \
              "where d.Bank_Name = \'" + bank + "\' and User_ID = \'" + user_id + "\'"
    cursor.execute(sql_str)
    employee_id = cursor.fetchall()[0][0]

    if balance < 0:
        flash('您有透支额，不允许销户')
        return redirect(url_for('check_account_customer', username=username))
    sql_str = "delete from employee_customer where User_ID = \'" + user_id + "\' and Employee_ID = \'" + employee_id + "\'"
    cursor.execute(sql_str)
    db.commit()
    sql_str = "delete from customer_checkaccount where User_ID = \'" + user_id + "\' and Bank_Name = \'" + bank + "\'"
    cursor.execute(sql_str)
    db.commit()
    sql_str = "delete from checkaccount where Account_ID = \'" + check_account_id + "\'"
    cursor.execute(sql_str)
    db.commit()
    flash('销户成功')
    return redirect(url_for('check_account_customer', username=username))


@app.route('/check_account_withdraw/<username>_<account_id>', methods=['GET', 'POST'])
def check_account_withdraw(username, account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    have_check_account = False

    sql_str = "select Account_ID from customer inner join customer_checkaccount cc on customer.User_ID = cc.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_id_list = cursor.fetchall()
    check_account_id_list = []
    for temp_id in temp_id_list:
        check_account_id_list.append(temp_id[0])

    sql_str = "select Account_balance, Overdraft from checkaccount where Account_ID =\'" + account_id + "\'"
    cursor.execute(sql_str)
    balance, overdraft = cursor.fetchall()[0]

    check_account_data = []
    if len(check_account_id_list):
        have_check_account = True
        for check_account_id in check_account_id_list:
            sql_str = "select * from checkaccount where Account_ID = \'" + check_account_id + "\'"
            cursor.execute(sql_str)
            check_account_data.append(cursor.fetchall()[0])

    if request.method == 'POST':
        amount = request.form['amount']
        if not amount.isdigit():
            flash("非法输入，取款失败，请输入数字")
            return redirect(url_for('check_account_withdraw', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，取款失败，请输入正数")
            return redirect(url_for('check_account_withdraw', username=username, account_id=account_id))
        elif balance - float(amount) < - overdraft:
            flash("透支额到达限度，取款失败")
            return redirect(url_for('check_account_withdraw', username=username, account_id=account_id))
        sql_str = "update checkaccount set Account_balance = Account_balance - " + amount
        cursor.execute(sql_str)
        db.commit()
        flash('取款成功')
        return redirect(url_for('check_account_customer', username=username))

    return render_template("check_account_withdraw.html", username=username, account_id=account_id,
                           have_check_account=have_check_account, check_account_data=check_account_data)


@app.route('/check_account_save/<username>_<account_id>', methods=['GET', 'POST'])
def check_account_save(username, account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    have_check_account = False

    sql_str = "select Account_ID from customer inner join customer_checkaccount cc on customer.User_ID = cc.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_id_list = cursor.fetchall()
    check_account_id_list = []
    for temp_id in temp_id_list:
        check_account_id_list.append(temp_id[0])

    check_account_data = []
    if len(check_account_id_list):
        have_check_account = True
        for check_account_id in check_account_id_list:
            sql_str = "select * from checkaccount where Account_ID = \'" + check_account_id + "\'"
            cursor.execute(sql_str)
            check_account_data.append(cursor.fetchall()[0])

    if request.method == 'POST':
        amount = request.form['amount']
        if not amount.isdigit():
            flash("非法输入，请输入数字")
            return redirect(url_for('check_account_save', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，请输入正数")
            return redirect(url_for('check_account_save', username=username, account_id=account_id))
        sql_str = "update checkaccount set Account_balance = Account_balance + " + amount
        cursor.execute(sql_str)
        db.commit()
        flash('存款成功')
        return redirect(url_for('check_account_customer', username=username))

    return render_template("check_account_save.html", username=username, account_id=account_id,
                           have_check_account=have_check_account, check_account_data=check_account_data)


# 客户端储蓄账户详情页
@app.route('/deposit_account_customer/<username>')
def deposit_account_customer(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    have_deposit_account = False

    # 根据用户名查询储蓄账户ID
    sql_str = "select Account_ID from customer inner join customer_depositaccount cd on customer.User_ID = cd.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_id_list = cursor.fetchall()
    deposit_account_id_list = []
    for temp_id in temp_id_list:
        deposit_account_id_list.append(temp_id[0])  # 该用户的储蓄账户ID列表

    deposit_account_data = []
    if len(deposit_account_id_list):
        have_deposit_account = True
        for deposit_account_id in deposit_account_id_list:
            # 账户ID，余额，开户日期，利率，货币种类
            sql_str = "select * from depositaccount where Account_ID = \'" + deposit_account_id + "\'"
            cursor.execute(sql_str)
            deposit_temp_data = cursor.fetchall()[0]
            deposit_temp_data = list(deposit_temp_data)
            if deposit_temp_data[5] == 0:
                deposit_temp_data[5] = "人民币"
            if deposit_temp_data[5] == 1:
                deposit_temp_data[5] = "美元"
            if deposit_temp_data[5] == 2:
                deposit_temp_data[5] = "欧元"
            if deposit_temp_data[5] == 3:
                deposit_temp_data[5] = "日元"
            deposit_account_data.append(deposit_temp_data)
        # flash(deposit_account_data)
        return render_template('deposit_account_customer.html', username=username,
                               have_deposit_account=have_deposit_account, deposit_account_data=deposit_account_data)
    else:
        return render_template('deposit_account_customer.html', username=username,
                               have_deposit_account=have_deposit_account, deposit_account_data=deposit_account_data)


@app.route('/open_deposit_account/<username>', methods=['GET', 'POST'])
def open_deposit_account(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    sql_str = "select Bank_Name from customer inner join customer_depositaccount cd on customer.User_ID = cd.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_bank_list = cursor.fetchall()
    open_bank_list = []
    for temp_bank in temp_bank_list:
        open_bank_list.append(temp_bank[0])

    if len(open_bank_list) == len(bank_list):
        flash("您已经在所有支行都注册了储蓄账户，无法再注册新账户")
        return redirect(url_for('deposit_account_customer', username=username))

    option_bank_list = copy.deepcopy(bank_list)  # python中直接用等号不是拷贝而是等价
    for item in open_bank_list:
        option_bank_list.remove(item)

    employee_dict = {}
    for option_bank in option_bank_list:
        employee_dict[option_bank] = []
        sql_str = "select Employee_Name,Employee_PhoneNumber,Is_Manager from employee " \
                  "inner join department d on employee.Department_ID = d.Department_ID " \
                  "inner join subbank s on d.Bank_Name = s.Bank_Name " \
                  "where d.Department_Name =\'客服部\' and d.Bank_Name = \'" + option_bank + "\'"
        cursor.execute(sql_str)
        option_employee_list = cursor.fetchall()
        for option_employee in option_employee_list:
            option_employee = list(option_employee)
            if option_employee[2] == 1:
                option_employee[2] = "经理"
            else:
                option_employee[2] = "员工"
            employee_dict[option_bank].append(option_employee)

    return render_template('open_deposit_account.html', username=username,
                           option_bank_list=option_bank_list, employee_dict=employee_dict, bank_list=bank_list)


@app.route('/build_deposit_account/<username>_<employee>_<bank>')
def build_deposit_account(username, employee, bank):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    user_id = cursor.fetchall()[0][0]

    sql_str = "select Employee_ID from employee where Employee_Name = \'" + employee + "\'"
    cursor.execute(sql_str)
    employee_id = cursor.fetchall()[0][0]

    sql_str = "select Account_ID from depositaccount"
    cursor.execute(sql_str)
    account_id_temp_list = cursor.fetchall()
    account_id_list = []
    # 获取ck后的数字位
    for item in account_id_temp_list:
        account_id_list.append(int(item[0][2:]))
    new_account_id = "ck" + str(max(account_id_list) + 1)

    sql_str = "insert into depositaccount " \
              "value (\'" + new_account_id + "\', 0, \'" + date + "\',\'" + bank + "\', 20000)"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "insert into customer_depositaccount " \
              "value (\'" + user_id + "\',\'" + bank + "\',\'" + new_account_id + "\',\'" + date + "\')"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "insert into employee_customer value (\'" + employee_id + "\',\'" + user_id + "\',\'ck\')"
    cursor.execute(sql_str)
    db.commit()

    flash("开户成功，跳转回储蓄账户界面")
    return redirect(url_for('deposit_account_customer', username=username))


@app.route('/delete_deposit_account/<username>_<deposit_account_id>_')
def delete_deposit_account(username, deposit_account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    user_id = cursor.fetchall()[0][0]

    sql_str = "select Account_balance,Reg_Bank from depositaccount where Account_ID = \'" + deposit_account_id + "\'"
    cursor.execute(sql_str)
    balance, bank = cursor.fetchall()[0]

    sql_str = "select Employee_ID from employee " \
              "inner join department d on employee.Department_ID = d.Department_ID " \
              "inner join subbank s on d.Bank_Name = s.Bank_Name " \
              "inner join customer_depositaccount cc on s.Bank_Name = cc.Bank_Name " \
              "where d.Bank_Name = \'" + bank + "\' and User_ID = \'" + user_id + "\'"
    cursor.execute(sql_str)
    employee_id = cursor.fetchall()[0][0]

    if balance < 0:
        flash('您有透支额，不允许销户')
        return redirect(url_for('deposit_account_customer', username=username))
    sql_str = "delete from employee_customer where User_ID = \'" + user_id + "\' and Employee_ID = \'" + employee_id + "\'"
    cursor.execute(sql_str)
    db.commit()
    sql_str = "delete from customer_depositaccount where User_ID = \'" + user_id + "\' and Bank_Name = \'" + bank + "\'"
    cursor.execute(sql_str)
    db.commit()
    sql_str = "delete from depositaccount where Account_ID = \'" + deposit_account_id + "\'"
    cursor.execute(sql_str)
    db.commit()
    flash('销户成功')
    return redirect(url_for('deposit_account_customer', username=username))


@app.route('/deposit_account_withdraw/<username>_<account_id>', methods=['GET', 'POST'])
def deposit_account_withdraw(username, account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    have_deposit_account = False

    sql_str = "select Account_ID from customer inner join customer_depositaccount cc on customer.User_ID = cc.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_id_list = cursor.fetchall()
    deposit_account_id_list = []
    for temp_id in temp_id_list:
        deposit_account_id_list.append(temp_id[0])

    deposit_account_data = []
    if len(deposit_account_id_list):
        have_deposit_account = True
        for deposit_account_id in deposit_account_id_list:
            sql_str = "select * from depositaccount where Account_ID = \'" + deposit_account_id + "\'"
            cursor.execute(sql_str)
            deposit_account_data.append(cursor.fetchall()[0])

    if request.method == 'POST':
        amount = request.form['amount']
        if not amount.isdigit():
            flash("非法输入，请输入数字")
            return redirect(url_for('deposit_account_withdraw', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，请输入正数")
            return redirect(url_for('deposit_account_withdraw', username=username, account_id=account_id))
        sql_str = "update depositaccount set Account_balance = Account_balance - " + amount
        cursor.execute(sql_str)
        db.commit()
        flash('取款成功')
        return redirect(url_for('deposit_account_customer', username=username))

    return render_template("deposit_account_withdraw.html", username=username, account_id=account_id,
                           have_deposit_account=have_deposit_account, deposit_account_data=deposit_account_data)


@app.route('/deposit_account_save/<username>_<account_id>', methods=['GET', 'POST'])
def deposit_account_save(username, account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    have_deposit_account = False

    sql_str = "select Account_ID from customer inner join customer_depositaccount cc on customer.User_ID = cc.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_id_list = cursor.fetchall()
    deposit_account_id_list = []
    for temp_id in temp_id_list:
        deposit_account_id_list.append(temp_id[0])

    deposit_account_data = []
    if len(deposit_account_id_list):
        have_deposit_account = True
        for deposit_account_id in deposit_account_id_list:
            sql_str = "select * from depositaccount where Account_ID = \'" + deposit_account_id + "\'"
            cursor.execute(sql_str)
            deposit_account_data.append(cursor.fetchall()[0])

    if request.method == 'POST':
        amount = request.form['amount']
        if not amount.isdigit():
            flash("非法输入，请输入数字")
            return redirect(url_for('deposit_account_save', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，请输入正数")
            return redirect(url_for('deposit_account_save', username=username, account_id=account_id))
        sql_str = "update depositaccount set Account_balance = Account_balance + " + amount
        cursor.execute(sql_str)
        db.commit()
        flash('存款成功')
        return redirect(url_for('deposit_account_customer', username=username))

    return render_template("deposit_account_save.html", username=username, account_id=account_id,
                           have_deposit_account=have_deposit_account, deposit_account_data=deposit_account_data)


if __name__ == '__main__':
    app.run(debug=True)
