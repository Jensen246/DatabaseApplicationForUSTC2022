from wtforms import Form, StringField, IntegerField, FileField, validators
from wtforms.validators import ValidationError, Length, EqualTo, Email, InputRequired, Regexp, NumberRange, URL, UUID
from email_validator import validate_email
import re  # 正则表达式验证

simple_type = {  # 客户属性
    "User_ID": "id", "User_Name": "name", "User_PhoneNumber": "phone",
    "User_Address": "address", "User_Contacts_Name": "name", "User_Contacts_PhoneNumber": "phone",
    "User_Contacts_Email": "email", "User_Contacts_Relation": "relation",
    # 员工属性
    "Employee_ID": "id", "Employee_Name": "name", "Employee_PhoneNumber": "phone", "Employee_Address": "address",
}


class RegisterForm(Form):  # 继承自Form，整个表单的验证
    """注册表单验证"""
    # validators:验证器，可多个，列表形式表示

    # 用户身份证号，5位整数
    user_id = StringField(validators=[Regexp(r'^[0-9]{5}$', message="身份证号必须为5位整数")])
    # 用户姓名，名字长度必须为2至30位
    user_name = StringField(validators=[Length(min=2, max=30, message="名字长度必须为2至30位")])
    # 电话号码验证，6到11位整数，手机号验证可以用：StringField(validators=[Regexp(r'1[34578]\d{9}', message='手机号格式错误')])
    user_phonenumber = StringField(validators=[Regexp(r'^[0-9]{6,11}$', message='电话号码格式错误')])
    # 地址验证，5到60位字符串
    user_address = StringField(validators=[Length(min=5, max=64, message="地址长度必须为5至60位")])

    # 联系人姓名验证
    user_contacts_name = StringField(validators=[Length(min=2, max=30, message="名字长度必须为2至30位")])
    # 联系人电话号码验证
    user_contacts_phonenumber = StringField(validators=[Regexp(r'^[0-9]{6,11}$', message='电话号码格式错误')])
    # 联系人邮箱验证
    user_contacts_email = StringField(validators=[Email(message="邮箱格式不正确")])  # message:错误提示信息
    # 联系人关系验证
    user_contacts_relation = StringField(validators=[Length(min=1, max=7, message="关系名必须为1到7位")])
    # 用户名验证
    username = StringField(validators=[InputRequired(message="您未输入")])
    # 密码验证
    password = StringField(validators=[Length(min=5, max=12, message="密码长度必须为5至12位")])
    # 重复密码验证
    password_rep = StringField(validators=[EqualTo('password', message="两次密码输入必须一致")])


def verify_edit(edit_type, verify_item):
    """
    验证单个属性，使用于编辑单个属性时
    :param edit_type: 编辑的类型
    :param verify_item: 待验证的数据
    :return: True通过，False不通过
    """
    # 身份证号
    if edit_type == "id":
        if verify_item.isdigit() and len(verify_item) == 5:
            return True
        else:
            return False
    # 姓名
    elif edit_type == "name":
        if 2 <= len(verify_item) <= 30:
            return True
        else:
            return False
    # 电话号码
    elif edit_type == "phone":
        if re.match(r'^\d{6,11}$', verify_item):
            return True
        else:
            return False
    # 地址
    elif edit_type == "address":
        if 5 <= len(verify_item) <= 60:
            return True
        else:
            return False
    # 邮箱
    elif edit_type == "email":
        try:
            validate_email(verify_item)
            return True
        except:
            return False
    # 关系
    elif edit_type == "relation":
        if 1 <= len(verify_item) <= 7:
            return True
        else:
            return False
