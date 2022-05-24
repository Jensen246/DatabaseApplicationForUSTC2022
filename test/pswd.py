from werkzeug.security import generate_password_hash, check_password_hash

psw = '123456'
psw_hsd = generate_password_hash(psw)
print(psw_hsd)
print(check_password_hash(psw_hsd,psw))
