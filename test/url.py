from flask import url_for

username = 'daniu'
r = url_for('index_employee', username=username)
print(r)
