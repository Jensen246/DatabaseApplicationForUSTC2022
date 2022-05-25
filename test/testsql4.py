from LoginManage import *

username = 'dahai'
password = '12345678'
flag = password_verify(username, password, 0)
print(flag)
password = '123456'
flag = password_verify(username, password, 0)
print(flag)
