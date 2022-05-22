::echo off ::

@echo off

echo 开始执行初始化脚本...

cd SQL

for %%i in {init_database.sql, init_bank.sql, init_employee.sql, init_customer.sql} do (

echo 正在执行 %%i 请稍后...

echo set names utf8;>all.sql

echo source %%i>>all.sql
)
mysql -u lqz -p 020406 --max_allowed_packet=1048576 --net_buffer_length=16384 bankapp < all.sql

echo %%i 执行完毕。



del all.sql

echo 所有脚本执行完毕。

pause