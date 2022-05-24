from wtforms import Form, StringField, IntegerField, FileField, validators
from wtforms.validators import ValidationError, Length, EqualTo, Email, InputRequired, Regexp, NumberRange, URL, UUID
from flask_wtf.file import FileRequired, FileAllowed

""" 表单验证 """


class RegisterForm(Form):  # 继承自Form
    """注册表单验证"""
    # validators:验证器，可多个，列表形式表示

    # 用户身份证号，5位整数
    user_id = StringField(validators=[Regexp(r'^[0-9]{5}$', message="身份证号为5位整数")])
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


class LoginForm(Form):
    """ 登录表单验证 """
    username = StringField(validators=[Length(min=6, max=12, message="用户名长度必须为6至12位")])
    pwd = StringField(validators=[Length(min=6, max=12, message="密码长度必须为6至12位")])

    captcha = StringField(validators=[Length(4, 4, message="验证码错误")])

    def validate_captcha(self, filed):
        """这里方法名必须validate_字段名，假设验证码为9850"""
        if filed.data != "9850":
            raise ValidationError("验证码错误")
