from flask import Flask, request, render_template, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
# from LoginManage import *
from DbProcess import *
from forms_verify import *
import copy
from IsFloat import isfloat
import datetime

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
    return render_template('index.html')


@app.route('/subbranch_index')
def subbranch_index():
    flash("您还没有登录,请先登录或注册")
    return render_template('subbranch_index.html', bank_list=bank_list)


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


@app.route('/open_check_account/<username>')
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
                  "where d.Department_Name =\'营销部\' and d.Bank_Name = \'" + option_bank + "\'"
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
        if not isfloat(amount):
            flash("非法输入，取款失败，请输入数字")
            return redirect(url_for('check_account_withdraw', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，取款失败，请输入正数")
            return redirect(url_for('check_account_withdraw', username=username, account_id=account_id))
        elif balance - float(amount) < - overdraft:
            flash("透支额到达限度，取款失败")
            return redirect(url_for('check_account_withdraw', username=username, account_id=account_id))
        sql_str = "update checkaccount set Account_balance = Account_balance - \'" + amount + \
                  "\' where Account_ID = \'" + account_id + "\'"
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
        if not isfloat(amount):
            flash("非法输入，请输入数字")
            return redirect(url_for('check_account_save', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，请输入正数")
            return redirect(url_for('check_account_save', username=username, account_id=account_id))
        sql_str = "update checkaccount set Account_balance = Account_balance + \'" + amount + \
                  "\' where Account_ID = \'" + account_id + "\'"
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


@app.route('/open_deposit_account_choose_currency_type/<username>', methods=['GET', 'POST'])
def open_deposit_account_choose_currency_type(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    if request.method == 'POST':
        currency_type = request.form['currency_type']
        return redirect(url_for('open_deposit_account', username=username, currency_type=currency_type))
    return render_template('open_deposit_account_choose_currency_type.html', username=username)


@app.route('/open_deposit_account/<username>_<currency_type>', methods=['GET', 'POST'])
def open_deposit_account(username, currency_type):
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
                  "where d.Department_Name =\'营销部\' and d.Bank_Name = \'" + option_bank + "\'"
        cursor.execute(sql_str)
        option_employee_list = cursor.fetchall()
        for option_employee in option_employee_list:
            option_employee = list(option_employee)
            if option_employee[2] == 1:
                option_employee[2] = "经理"
            else:
                option_employee[2] = "员工"
            employee_dict[option_bank].append(option_employee)

    return render_template('open_deposit_account.html', username=username, currency_type=currency_type,
                           option_bank_list=option_bank_list, employee_dict=employee_dict, bank_list=bank_list)


@app.route('/build_deposit_account/<username>_<employee>_<bank>_<currency_type>', methods=['GET', 'POST'])
def build_deposit_account(username, employee, bank, currency_type):
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
    # 获取dp后的数字位
    for item in account_id_temp_list:
        account_id_list.append(int(item[0][2:]))
    new_account_id = "dp" + str(max(account_id_list) + 1)

    flash(currency_type)

    sql_str = "insert into depositaccount " \
              "value (\'" + new_account_id + "\', 0, \'" + date + "\',\'" + bank + "\', 0.03," + currency_type + ")"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "insert into customer_depositaccount " \
              "value (\'" + user_id + "\',\'" + bank + "\',\'" + new_account_id + "\',\'" + date + "\')"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "insert into employee_customer value (\'" + employee_id + "\',\'" + user_id + "\',\'dp\')"
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

    sql_str = "select Account_ID from customer inner join customer_depositaccount cd on customer.User_ID = cd.User_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    temp_id_list = cursor.fetchall()
    deposit_account_id_list = []
    for temp_id in temp_id_list:
        deposit_account_id_list.append(temp_id[0])

    sql_str = "select Account_balance from depositaccount where Account_ID =\'" + account_id + "\'"
    cursor.execute(sql_str)
    balance = cursor.fetchall()[0][0]

    deposit_account_data = []
    if len(deposit_account_id_list):
        have_deposit_account = True
        for deposit_account_id in deposit_account_id_list:
            sql_str = "select * from depositaccount where Account_ID = \'" + deposit_account_id + "\'"
            cursor.execute(sql_str)
            deposit_account_data.append(cursor.fetchall()[0])

    if request.method == 'POST':
        amount = request.form['amount']
        if not isfloat(amount):
            flash("非法输入，取款失败，请输入数字")
            return redirect(url_for('deposit_account_withdraw', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，取款失败，请输入正数")
            return redirect(url_for('deposit_account_withdraw', username=username, account_id=account_id))
        elif balance - float(amount) < 0:
            flash("余额不足，取款失败")
            return redirect(url_for('deposit_account_withdraw', username=username, account_id=account_id))
        sql_str = "update depositaccount set Account_balance = Account_balance - \'" + amount + \
                  "\' where Account_ID = \'" + account_id + "\'"
        cursor.execute(sql_str)
        db.commit()
        flash('取款成功')
        return redirect(url_for('deposit_account_customer', username=username))

    return render_template("deposit_account_withdraw.html", username=username, account_id=account_id,
                           have_deposit_account=have_deposit_account, deposit_account_data=deposit_account_data)


# 储蓄账户存款
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
        if not isfloat(amount):
            flash("非法输入，请输入数字")
            return redirect(url_for('deposit_account_save', username=username, account_id=account_id))
        elif float(amount) < 0:
            flash("非法输入，请输入正数")
            return redirect(url_for('deposit_account_save', username=username, account_id=account_id))
        sql_str = "update depositaccount set Account_balance = Account_balance + \'" + amount + \
                  "\' where Account_ID = \'" + account_id + "\'"
        cursor.execute(sql_str)
        db.commit()
        flash('存款成功')
        return redirect(url_for('deposit_account_customer', username=username))

    return render_template("deposit_account_save.html", username=username, account_id=account_id,
                           have_deposit_account=have_deposit_account, deposit_account_data=deposit_account_data)


# 客户请求新贷款
@app.route('/loan_request_customer/<username>', methods=['GET', 'POST'])
def loan_request_customer(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    user_id = cursor.fetchall()[0][0]

    if request.method == 'POST':
        bank = request.form['bank']  # 要贷款的支行
        loan_money = request.form['loan_money']  # 请求的贷款额度

        if not isfloat(loan_money):
            flash("非法输入，请输入数字")
            return redirect(url_for('loan_request_customer', username=username, bank_list=bank_list))
        elif float(loan_money) < 0:
            flash("非法输入，请输入正数")
            return redirect(url_for('loan_request_customer', username=username, bank_list=bank_list))
        # 查询当前最大的贷款ln id生成新的贷款号
        sql_str = "select Loan_ID from loan"
        cursor.execute(sql_str)
        loan_id_temp_list = cursor.fetchall()
        loan_id_list = []
        # 获取ln后的数字位
        for item in loan_id_temp_list:
            loan_id_list.append(int(item[0][2:]))
        new_loan_id = "ln" + str(max(loan_id_list) + 1)

        sql_str = "insert into loan value ( \'" + new_loan_id + "\',\'" + bank + "\',\'" + loan_money + "\',\'0\')"
        cursor.execute(sql_str)
        db.commit()
        sql_str = "insert into customer_loan value (\'" + new_loan_id + "\',\'" + user_id + "\')"
        cursor.execute(sql_str)
        db.commit()
        # 由于贷款业务没有规定数量上限，所以限定每个客户绑定一个负责其贷款业务的员工
        sql_str = "select * from employee_customer " \
                  "inner join employee e on employee_customer.Employee_ID = e.Employee_ID " \
                  "inner join department d on e.Department_ID = d.Department_ID " \
                  "where Service_Type = \'ln\' and User_ID = \'" + user_id + "\' and d.Bank_Name = \'" + bank + "\'"
        cursor.execute(sql_str)
        flag = cursor.fetchall()
        if not len(flag):
            flash("发起贷款成功，但您需要选择负责您贷款业务的员工")
            return redirect(url_for("loan_choose_employee_customer", username=username, bank=bank))
        else:
            flash("发起贷款成功，跳转到贷款详情页")
            return redirect(url_for("loan_customer_info", username=username))
    return render_template('loan_request_customer.html', username=username, bank_list=bank_list)


# 客户选择与他绑定贷款业务的员工
@app.route('/loan_choose_employee_customer/<username>_<bank>')
def loan_choose_employee_customer(username, bank):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    sql_str = "select Employee_Name,Employee_PhoneNumber,Is_Manager,Employee_Username from employee " \
              "inner join department d on employee.Department_ID = d.Department_ID " \
              "where Bank_Name = \'" + bank + "\' and Department_Name = \'客服部\'"
    cursor.execute(sql_str)
    employee_data = cursor.fetchall()
    employee_list = []
    for employee in employee_data:
        if employee[2] == 1:
            flag = '经理'
        else:
            flag = "员工"
        employee_list.append([employee[0], str(employee[1]), flag, employee[3]])
    return render_template("loan_choose_employee_customer.html", username=username, bank=bank,
                           employee_list=employee_list)


@app.route('/loan_add_employee_customer/<username>_<employee>')
def loan_add_employee_customer(username, employee):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    sql_str = "select User_ID from customer where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    user_id = cursor.fetchall()[0][0]
    sql_str = "select Employee_ID from employee where Employee_Username = \'" + employee + "\'"
    cursor.execute(sql_str)
    employee_id = cursor.fetchall()[0][0]
    sql_str = "insert into employee_customer value (\'" + employee_id + "\',\'" + user_id + "\',\'ln\')"
    cursor.execute(sql_str)
    db.commit()
    flash("设置贷款负责人成功，跳转到贷款详情页")
    return redirect(url_for("loan_customer_info", username=username))


# 客户端贷款详情页，显示客户的所有贷款业务
@app.route('/loan_customer_info/<username>')
def loan_customer_info(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    sql_str = "select loan.Loan_ID, Bank_Name, Loan_Money, Loan_Status from loan " \
              "inner join customer_loan cl on loan.Loan_ID = cl.Loan_ID " \
              "inner join customer c on cl.User_ID = c.User_ID" \
              " where User_Username=\'" + username + "\'"
    cursor.execute(sql_str)
    loan_info_data = cursor.fetchall()
    loan_info_list = []
    for loan_info in loan_info_data:
        loan_info_list.append(list(loan_info))
    for loan_info in loan_info_list:
        if loan_info[3] == 0:
            loan_info[3] = "未发放"
        elif loan_info[3] == 1:
            loan_info[3] = '发放中'
        elif loan_info[3] == 2:
            loan_info[3] = "发放完成"
    return render_template("loan_customer_info.html", username=username, loan_info_list=loan_info_list)


@app.route('/loan_delete/<username>_<loan_id>')
def loan_delete(username, loan_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select Loan_Status from loan where Loan_ID = \'" + loan_id + "\'"
    cursor.execute(sql_str)
    flag = cursor.fetchall()[0][0]
    if not flag:
        flash("该贷款尚未发放完成，不允许删除")
        return redirect(url_for('loan_customer_info', username=username))
    sql_str = "delete from customer_loan where Loan_ID = \'" + loan_id + "\'"
    cursor.execute(sql_str)
    db.commit()

    flash("删除成功")
    return redirect(url_for('loan_customer_info', username=username))


@app.route('/employee_relate_customer/<username>')
def employee_relate_customer(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    sql_str = "select ec.User_ID, ec.Employee_ID, Employee_Name, Employee_PhoneNumber, Service_Type,Is_Manager, Bank_Name " \
              "from employee inner join employee_customer ec on employee.Employee_ID = ec.Employee_ID " \
              "inner join customer c on ec.User_ID = c.User_ID " \
              "inner join department d on employee.Department_ID = d.Department_ID " \
              "where User_Username = \'" + username + "\'"
    cursor.execute(sql_str)
    relation_temp_data = cursor.fetchall()
    relation_list = []
    for item in relation_temp_data:
        relation_list.append(list(item))
    for item in relation_list:
        if item[4] == 'ck':
            item[4] = '支票账户'
        elif item[4] == 'dp':
            item[4] = '储蓄账户'
        elif item[4] == 'ln':
            item[4] = '贷款业务'
        if item[5] == 1:
            item[5] = '经理'
        else:
            item[5] = "员工"
    return render_template("employee_relate_customer.html", username=username, relation_list=relation_list)


@app.route('/employee_relate_customer_change/<username>_<user_id>/<bank>_<service_type>_<old_employee>')
def employee_relate_customer_change(username, user_id, bank, service_type, old_employee):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    if service_type == "贷款业务":
        department = '客服部'
    else:
        department = '营销部'
    sql_str = "select Employee_Name,Employee_PhoneNumber,Is_Manager,Employee_ID from employee " \
              "inner join department d on employee.Department_ID = d.Department_ID " \
              "where Department_Name = \'" + department + "\' and Bank_Name = \'" + bank + "\'"
    cursor.execute(sql_str)
    employee_temp_data = cursor.fetchall()
    employee_data_list = []
    for item in employee_temp_data:
        employee_data_list.append(list(item))
    for item in employee_data_list:
        if item[2] == 1:
            item[2] = '经理'
        else:
            item[2] = '员工'
    return render_template("employee_relate_customer_change.html",
                           username=username, employee_data_list=employee_data_list, old_employee=old_employee,
                           user_id=user_id, service_type=service_type, bank=bank)


@app.route('/employee_relate_customer_update/<username>_<user_id>/<service_type>/<old_employee>_to_<new_employee>')
def employee_relate_customer_update(username, user_id, service_type, old_employee, new_employee):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    if service_type == "支票账户":
        service_str = "ck"
    elif service_type == "储蓄账户":
        service_str = "dp"
    else:
        service_str = "ln"
    sql_str = "delete from employee_customer " \
              "where Employee_ID = \'" + old_employee + \
              "\' and User_ID = \'" + user_id + \
              "\' and Service_Type = \'" + service_str + "\'"
    cursor.execute(sql_str)
    db.commit()
    flash("成功删除旧责任关系")
    sql_str = "insert into employee_customer " \
              "value (\'" + new_employee + "\',\'" + user_id + "\',\'" + service_str + "\')"
    cursor.execute(sql_str)
    db.commit()
    flash("成功添加新责任关系，跳转关联负责员工界面")
    return redirect(url_for('employee_relate_customer', username=username))


@app.route("/customer_info_employee/<username>", methods=['GET', 'POST'])
def customer_info_employee(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select * from customer"
    cursor.execute(sql_str)
    customer_data = cursor.fetchall()
    customer_list = []
    for item in customer_data:
        customer_list.append(list(item))
    if request.method == 'POST':
        name = request.form["name"]
        address = request.form["address"]
        contacts_name = request.form["contacts_name"]

        if not (name or address or contacts_name):
            return render_template("customer_info_employee.html", username=username, customer_data=customer_data)
        else:
            customer_list_name = copy.deepcopy(customer_list)
            customer_list_address = copy.deepcopy(customer_list)
            customer_list_contacts_name = copy.deepcopy(customer_list)
            if name:
                customer_list_name = []
                sql_str = "select * from customer where User_Name like \'%" + name + "%\'"
                cursor.execute(sql_str)
                customer_data_name = cursor.fetchall()
                for item in customer_data_name:
                    customer_list_name.append(list(item))
            if address:
                customer_list_address = []
                sql_str = "select * from customer where User_Address like \'%" + address + "%\'"
                cursor.execute(sql_str)
                customer_data_address = cursor.fetchall()
                for item in customer_data_address:
                    customer_list_address.append(list(item))
            if contacts_name:
                customer_list_contacts_name = []
                sql_str = "select * from customer where User_Contacts_Name like \'%" + contacts_name + "%\'"
                cursor.execute(sql_str)
                customer_data_contacts_name = cursor.fetchall()
                for item in customer_data_contacts_name:
                    customer_list_contacts_name.append(list(item))
            customer_result_list = []
            for customer in customer_list_name:
                if customer in customer_list_address:
                    if customer in customer_list_contacts_name:
                        customer_result_list.append(customer)
            """flash(customer_list)
            flash(customer_list_address)
            flash(customer_result_list)"""
            return render_template("customer_info_employee.html", username=username, customer_data=customer_result_list)

    return render_template("customer_info_employee.html", username=username, customer_data=customer_data)


@app.route("/deposit_account_employee/<username>", methods=['GET', 'POST'])
def deposit_account_employee(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    currency_show = ['人民币', '美元', '欧元', '日元']
    sql_str = "select cd.Account_ID,c.User_ID,c.User_Name,Account_balance,Reg_Bank,Currency_type,Interest_Rate " \
              "from depositaccount " \
              "inner join customer_depositaccount cd on depositaccount.Account_ID = cd.Account_ID " \
              "inner join customer c on cd.User_ID = c.User_ID"
    cursor.execute(sql_str)
    deposit_account_data = cursor.fetchall()
    deposit_account_list = []
    for item in deposit_account_data:
        deposit_account_list.append(list(item))
    if request.method == 'POST':
        name = request.form["name"]
        bank = request.form["bank"]
        currency_type = request.form["currency_type"]
        flag_name = flag_bank = flag_currency = 0
        if name:
            flag_name = 1
            account_list_name = []
            sql_str = "select Account_ID from customer " \
                      "inner join customer_depositaccount on customer.User_ID = customer_depositaccount.User_ID " \
                      "where User_Name like \'%" + name + "%\'"
            cursor.execute(sql_str)
            data_name = cursor.fetchall()
            for item in data_name:
                account_list_name.append(item[0])
        if bank != '-1':
            flag_bank = 1
            account_list_bank = []
            sql_str = "select Account_ID from depositaccount where Reg_Bank = \'" + bank + "\'"
            cursor.execute(sql_str)
            data_bank = cursor.fetchall()
            for item in data_bank:
                account_list_bank.append(item[0])
        if currency_type != '-1':
            flag_currency = 1
            account_list_currency = []
            sql_str = "select Account_ID from depositaccount where Currency_type = \'" + currency_type + "\'"
            cursor.execute(sql_str)
            data_currency = cursor.fetchall()
            for item in data_currency:
                account_list_currency.append(item[0])

        sql_str = "select Account_ID from depositaccount"
        cursor.execute(sql_str)
        account_data = cursor.fetchall()
        account_list = []
        for item in account_data:
            account_list.append(item[0])

        if flag_name == 0:
            account_list_name = copy.deepcopy(account_list)
        if flag_bank == 0:
            account_list_bank = copy.deepcopy(account_list)
        if flag_currency == 0:
            account_list_currency = copy.deepcopy(account_list)

        """flash(account_list)
        flash(account_list_name)
        flash(account_list_currency)
        flash(account_list_bank)"""

        result_list = []
        for item in deposit_account_list:
            # flash(item)
            if item[0] in account_list_bank:
                if item[0] in account_list_name:
                    if item[0] in account_list_currency:
                        result_list.append(item)
        # flash(result_list)
        return render_template("deposit_account_employee.html", username=username, currency_show=currency_show,
                               deposit_account_data=result_list, bank_list=bank_list)

    return render_template("deposit_account_employee.html", username=username, currency_show=currency_show,
                           deposit_account_data=deposit_account_data, bank_list=bank_list)


@app.route("/deposit_interest_change/<username>/<account_id>", methods=['GET', 'POST'])
def deposit_interest_change(username, account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    flash("当前修改的账户号：" + account_id)
    if request.method == 'POST':
        new_interest = request.form['new_interest']
        # flash(new_interest)
        if not isfloat(new_interest):
            flash("请输入数字")
            return redirect(url_for("deposit_interest_change", username=username, account_id=account_id))
        if float(new_interest) < 0 or float(new_interest) > 1:
            flash("利率要求在0到1之间")
            return redirect(url_for("deposit_interest_change", username=username, account_id=account_id))
        sql_str = "update depositaccount set Interest_Rate = \'" + new_interest + \
                  "\' where Account_ID = \'" + account_id + "\'"
        cursor.execute(sql_str)
        db.commit()
        flash("成功变更利率，跳转储蓄账户页")
        return redirect(url_for("deposit_account_employee", username=username))
    return render_template("deposit_interest_change.html", username=username, account_id=account_id)


@app.route("/check_account_employee/<username>", methods=['GET', 'POST'])
def check_account_employee(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))
    sql_str = "select cc.Account_ID,c.User_ID,c.User_Name,Account_balance,Reg_Bank,Overdraft " \
              "from checkaccount " \
              "inner join customer_checkaccount cc on checkaccount.Account_ID = cc.Account_ID " \
              "inner join customer c on cc.User_ID = c.User_ID"
    cursor.execute(sql_str)
    check_account_data = cursor.fetchall()
    check_account_list = []
    for item in check_account_data:
        check_account_list.append(list(item))
    if request.method == 'POST':
        name = request.form["name"]
        bank = request.form["bank"]

        flag_name = flag_bank = 0
        if name:
            flag_name = 1
            account_list_name = []
            sql_str = "select Account_ID from customer " \
                      "inner join customer_checkaccount on customer.User_ID = customer_checkaccount.User_ID " \
                      "where User_Name like \'%" + name + "%\'"
            cursor.execute(sql_str)
            data_name = cursor.fetchall()
            for item in data_name:
                account_list_name.append(item[0])
        if bank != '-1':
            flag_bank = 1
            account_list_bank = []
            sql_str = "select Account_ID from checkaccount where Reg_Bank = \'" + bank + "\'"
            cursor.execute(sql_str)
            data_bank = cursor.fetchall()
            for item in data_bank:
                account_list_bank.append(item[0])

        sql_str = "select Account_ID from checkaccount"
        cursor.execute(sql_str)
        account_data = cursor.fetchall()
        account_list = []
        for item in account_data:
            account_list.append(item[0])

        if flag_name == 0:
            account_list_name = copy.deepcopy(account_list)
        if flag_bank == 0:
            account_list_bank = copy.deepcopy(account_list)

        result_list = []
        for item in check_account_list:
            # flash(item)
            if item[0] in account_list_bank:
                if item[0] in account_list_name:
                    result_list.append(item)
        # flash(result_list)
        return render_template("check_account_employee.html", username=username,
                               check_account_data=result_list, bank_list=bank_list)

    return render_template("check_account_employee.html", username=username,
                           check_account_data=check_account_data, bank_list=bank_list)


@app.route("/check_overdraft_change/<username>/<account_id>", methods=['GET', 'POST'])
def check_overdraft_change(username, account_id):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    flash("当前修改的账户号是：" + account_id)
    sql_str = "select Account_balance from checkaccount where Account_ID = \'" + account_id + "\'"
    cursor.execute(sql_str)
    balance = cursor.fetchall()[0][0]
    if balance < 0:
        flash("当前账户已经透支的金额为" + str(-float(balance)))
    else:
        flash("该账户暂无透支金额")
    if request.method == 'POST':
        new_overdraft = request.form['new_overdraft']
        # flash(new_overdraft)
        if not isfloat(new_overdraft):
            flash("请输入数字")
            return redirect(url_for("check_overdraft_change", username=username, account_id=account_id))
        # 透支额度修改后不能比已经透支的金额更小

        if float(new_overdraft) < 0:
            flash("请输入正数")
            return redirect(url_for("check_overdraft_change", username=username, account_id=account_id))
        if balance < 0 and float(new_overdraft) < -balance:
            flash("透支额度不能小于已经透支的金额")
            return redirect(url_for("check_overdraft_change", username=username, account_id=account_id))
        sql_str = "update checkaccount set Overdraft = \'" + new_overdraft + \
                  "\' where Account_ID = \'" + account_id + "\'"
        cursor.execute(sql_str)
        db.commit()
        flash("成功变更透支额度，跳转储蓄账户页")
        return redirect(url_for("check_account_employee", username=username))
    return render_template("check_overdraft_change.html", username=username, account_id=account_id)


@app.route('/loan_employee/<username>', methods=['GET', 'POST'])
def loan_employee(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    show_loan_status = ["未发放", "发放中", "发放完成"]
    sql_str = "select cl.Loan_ID,c.User_ID,c.User_Name,Bank_Name,Loan_Money,Loan_Status " \
              "from loan inner join customer_loan cl on loan.Loan_ID = cl.Loan_ID " \
              "inner join customer c on cl.User_ID = c.User_ID order by Loan_Status ASC "
    cursor.execute(sql_str)
    loan_data = cursor.fetchall()
    loan_list = []
    for item in loan_data:
        loan_list.append(list(item))
    # 计算已经支付的金额
    for item in loan_list:
        payed_money = 0
        loan_id = item[0]
        sql_str = "select Pay_Money from payment where Loan_ID = \'" + loan_id + "\'"
        cursor.execute(sql_str)
        pay_data = cursor.fetchall()
        for pay_item in pay_data:
            payed_money = payed_money + pay_item[0]
        item.append(payed_money)
    if request.method == 'POST':
        name = request.form['name']
        bank = request.form['bank']
        status = request.form['status']

        flag_name = flag_bank = flag_status = 0
        if name:
            flag_name = 1
            loan_list_name = []
            sql_str = "select loan.Loan_ID from loan " \
                      "inner join customer_loan cl on loan.Loan_ID = cl.Loan_ID " \
                      "inner join customer c on c.User_ID = cl.User_ID " \
                      "where c.User_Name like \'%" + name + "%\'"
            cursor.execute(sql_str)
            data_name = cursor.fetchall()
            for item in data_name:
                loan_list_name.append(item[0])
        if bank != '-1':
            flag_bank = 1
            loan_list_bank = []
            sql_str = "select Loan_ID from loan where Bank_Name = \'" + bank + "\'"
            cursor.execute(sql_str)
            data_bank = cursor.fetchall()
            for item in data_bank:
                loan_list_bank.append(item[0])
        if status != '-1':
            flag_status = 1
            loan_list_status = []
            sql_str = "select Loan_ID from loan where Loan_Status = \'" + status + "\'"
            cursor.execute(sql_str)
            data_status = cursor.fetchall()
            for item in data_status:
                loan_list_status.append(item[0])

        sql_str = "select Loan_ID from loan"
        cursor.execute(sql_str)
        loan_id_data = cursor.fetchall()
        loan_id_list = []
        for item in loan_id_data:
            loan_id_list.append(item[0])

        if flag_name == 0:
            loan_list_name = copy.deepcopy(loan_id_list)
        if flag_bank == 0:
            loan_list_bank = copy.deepcopy(loan_id_list)
        if flag_status == 0:
            loan_list_status = copy.deepcopy(loan_id_list)

        result_list = []
        for item in loan_list:
            if item[0] in loan_list_name:
                if item[0] in loan_list_bank:
                    if item[0] in loan_list_status:
                        result_list.append(item)
        return render_template("loan_employee.html", bank_list=bank_list,
                               username=username, loan_list=result_list, show_loan_status=show_loan_status)

    return render_template("loan_employee.html", bank_list=bank_list,
                           username=username, loan_list=loan_list, show_loan_status=show_loan_status)


@app.route('/pay_loan/<username>_<loan_id>/<loan_money>_<payed_money>_<status>', methods=['GET', 'POST'])
def pay_loan(username, loan_id, loan_money, payed_money, status):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    rest_money = float(loan_money) - float(payed_money)
    flash("贷款号" + loan_id + "：待支付金额为 " + str(rest_money))
    if request.method == 'POST':
        pay_money = request.form['pay_money']
        if not isfloat(pay_money):
            flash("请输入数字")
            return redirect(url_for("pay_loan", status=status,
                                    username=username, loan_id=loan_id, loan_money=loan_money, payed_money=payed_money))
        if float(pay_money) < 0:
            flash("请输入正数")
            return redirect(url_for("pay_loan", status=status,
                                    username=username, loan_id=loan_id, loan_money=loan_money, payed_money=payed_money))
        if float(pay_money) > rest_money:
            flash("发放金额不能大于待支付金额")
            return redirect(url_for("pay_loan", status=status,
                                    username=username, loan_id=loan_id, loan_money=loan_money, payed_money=payed_money))
        sql_str = "insert into payment value (\'" + loan_id + "\',\'" + date + "\',\'" + pay_money + "\')"
        cursor.execute(sql_str)
        db.commit()
        if status == '0':
            sql_str = "update loan set Loan_Status = 1 where Loan_ID =\'" + loan_id + "\'"
            cursor.execute(sql_str)
            db.commit()
        if pay_money == rest_money:
            sql_str = "update loan set Loan_Status = 2 where Loan_ID =\'" + loan_id + "\'"
            cursor.execute(sql_str)
            db.commit()
        flash("发放完成，回到贷款业务管理页面")
        return redirect(url_for("loan_employee", username=username))
    return render_template("pay_loan.html", username=username)


@app.route("/statistics/<username>")
def statistics(username):
    permission = session.get(username)
    if not permission:
        flash('非法请求，跳转到初始页')
        return redirect(url_for('index'))

    # 通过子串匹配确定是否为同一月度/季度/年度，下面三个函数分别以字符串形式返回待匹配的子串
    def get_year(date_in_data):
        return str(date_in_data)[:4]

    def get_month(date_in_data):
        return str(date_in_data)[:7]

    def get_quarter(date_in_data):
        year = get_year(date_in_data)
        month = int(date_in_data.month)
        quarter = (month - 1) // 3 + 1
        return (str(year) + "-" + str(quarter))

    sql_str = "select Account_balance,Reg_Date,Reg_Bank from depositaccount"
    cursor.execute(sql_str)
    deposit_data = cursor.fetchall()
    sql_str = "select Account_balance,Reg_Date,Reg_Bank from checkaccount"
    cursor.execute(sql_str)
    check_data = cursor.fetchall()
    sql_str = "select Pay_money,Pay_Date,l.Bank_Name from payment inner join loan l on payment.Loan_ID = l.Loan_ID"
    cursor.execute(sql_str)
    loan_data = cursor.fetchall()

    # 年度
    year_dict_deposit = {}
    for item in deposit_data:
        year = get_year(item[1])
        bank = item[2]
        if not year_dict_deposit.get(bank):
            year_dict_deposit[bank] = {}
        if not year_dict_deposit[bank].get(year):
            year_dict_deposit[bank][year] = float(item[0])
        else:
            year_dict_deposit[bank][year] += float(item[0])
    # 季度
    quarter_dict_deposit = {}
    for item in deposit_data:
        quarter = get_quarter(item[1])
        bank = item[2]
        if not quarter_dict_deposit.get(bank):
            quarter_dict_deposit[bank] = {}
        if not quarter_dict_deposit[bank].get(quarter):
            quarter_dict_deposit[bank][quarter] = float(item[0])
        else:
            quarter_dict_deposit[bank][quarter] += float(item[0])
    # 月度
    month_dict_deposit = {}
    for item in deposit_data:
        month = get_month(item[1])
        bank = item[2]
        if not month_dict_deposit.get(bank):
            month_dict_deposit[bank] = {}
        if not month_dict_deposit[bank].get(month):
            month_dict_deposit[bank][month] = float(item[0])
        else:
            month_dict_deposit[bank][month] += float(item[0])

    # 年度
    year_dict_check = {}
    for item in check_data:
        year = get_year(item[1])
        bank = item[2]
        if not year_dict_check.get(bank):
            year_dict_check[bank] = {}
        if not year_dict_check[bank].get(year):
            year_dict_check[bank][year] = float(item[0])
        else:
            year_dict_check[bank][year] += float(item[0])
    # 季度
    quarter_dict_check = {}
    for item in check_data:
        quarter = get_quarter(item[1])
        bank = item[2]
        if not quarter_dict_check.get(bank):
            quarter_dict_check[bank] = {}
        if not quarter_dict_check[bank].get(quarter):
            quarter_dict_check[bank][quarter] = float(item[0])
        else:
            quarter_dict_check[bank][quarter] += float(item[0])
    # 月度
    month_dict_check = {}
    for item in check_data:
        month = get_month(item[1])
        bank = item[2]
        if not month_dict_check.get(bank):
            month_dict_check[bank] = {}
        if not month_dict_check[bank].get(month):
            month_dict_check[bank][month] = float(item[0])
        else:
            month_dict_check[bank][month] += float(item[0])

    # 年度
    year_dict_loan = {}
    for item in loan_data:
        year = get_year(item[1])
        bank = item[2]
        if not year_dict_loan.get(bank):
            year_dict_loan[bank] = {}
        if not year_dict_loan[bank].get(year):
            year_dict_loan[bank][year] = float(item[0])
        else:
            year_dict_loan[bank][year] += float(item[0])
    # 季度
    quarter_dict_loan = {}
    for item in loan_data:
        quarter = get_quarter(item[1])
        bank = item[2]
        if not quarter_dict_loan.get(bank):
            quarter_dict_loan[bank] = {}
        if not quarter_dict_loan[bank].get(quarter):
            quarter_dict_loan[bank][quarter] = float(item[0])
        else:
            quarter_dict_loan[bank][quarter] += float(item[0])
    # 月度
    month_dict_loan = {}
    for item in loan_data:
        month = get_month(item[1])
        bank = item[2]
        if not month_dict_loan.get(bank):
            month_dict_loan[bank] = {}
        if not month_dict_loan[bank].get(month):
            month_dict_loan[bank][month] = float(item[0])
        else:
            month_dict_loan[bank][month] += float(item[0])

    return render_template("statistics.html", username=username,
                           year_dict_deposit=year_dict_deposit,
                           month_dict_deposit=month_dict_deposit,
                           quarter_dict_deposit=quarter_dict_deposit,
                           year_dict_check=year_dict_check,
                           month_dict_check=month_dict_check,
                           quarter_dict_check=quarter_dict_check,
                           year_dict_loan=year_dict_loan,
                           month_dict_loan=month_dict_loan,
                           quarter_dict_loan=quarter_dict_loan)


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码


if __name__ == '__main__':
    app.run(debug=True)
