# DatabaseApplicationForUSTC2022
USTC2022数据库系统及应用实验三
B/S架构
`MySQL`+`Flask`+`Jinja2`+`html`+`css`

ps：刚刚检查发现贷款删除部分删除发放中贷款以及支票账户部分的取款按钮显示似乎还有点小bug，偷个懒就不改了doge

## 项目启动方法

* 初始化数据库：

  不要求实现支行、部门和员工信息这三类数据的维护，但在程序开始运行之前需要插入这些数据，用命令行连接MySQL运行`batch_init.sql`即可，登录时将默认编码设置为`utf8`以免出现乱码：

  ```mysql
  mysql -u root -p --default-character-set=utf8
  password:******
  > source batch_init.sql
  ```

  该程序调用了多个sql文件，其中：

  * `init_database.sql`用于建库
  * `init_bank.sql`用于插入支行和部门
  * `init_employee.sql`用于初始化员工（包括初始化员工的登录用户名密码）
  * `init_customer.sql`用于插入一部分客户和他们的储蓄与支票账户记录
  * `init_loan.sql`用来插入一部分客户的贷款记录以及贷款的部分发放记录

  数据库初始化的数据在参考[学长代码](https://github.com/isaacveg/USTC_2021_DatabaseLab/tree/main/lab3)的基础上针对自己的数据库结构做了一点修改，其他部分均为原创

* 若需要将代码部署到其他环境下运行，只需`git clone`，在项目路径下建立一个新的`pipenv`，通过`pipenv install Pipfile`即可安装依赖

* 部署到Linux系统上运行需要注意的有：

  * 使用`pymysql`库，安装`MySQLdb`过程中会出现`ConfigParse`库由于python版本问题大小写不一致导致安装失败

  * Windows系统MySQL默认关闭大小写敏感，Linux系统默认开启大小写敏感，网上给出的方法大多数是修改`mysqld.cnf`文件，但`MySQL8.0`以后不再支持修改配置文件，必须在初始化时就指定好配置，我参考的是以下链接给出的第二个方法：[lowercase - lower_case_table_names=1 on Ubuntu 18.04 doesn't let mysql to start - Stack Overflow](https://stackoverflow.com/questions/53103588/lower-case-table-names-1-on-ubuntu-18-04-doesnt-let-mysql-to-start)

    This worked for me on a fresh Ubuntu Server 20.04 installation with MySQL 8.0.20 (no existing databases to care about - so if you have important data then you should backup/export it elsewhere before doing this):

    So... I did everything with elevated permissions:

    ```bash
    sudo su
    ```

    Install MySQL (if not already installed):

    ```shell
    apt-get install mysql-server
    ```

    Backup configuration file, uninstall it, delete all databases and MySQL related data:

    ```bash
    cp /etc/mysql/mysql.conf.d/mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf.backup
    service mysql stop
    apt-get --purge autoremove mysql-server
    rm -R /var/lib/mysql
    ```

    Restore saved configuration file, edit the file (add a line just under [mysqld] line):

    ```bash
    cp /etc/mysql/mysql.conf.d/mysqld.cnf.backup /etc/mysql/mysql.conf.d/mysqld.cnf
    vim /etc/mysql/mysql.conf.d/mysqld.cnf
    
    ...
    lower_case_table_names=1
    ...
    ```

    Reinstall MySQL (keeping the configuration file), configure additional settings:

    ```sql
    apt-get install mysql-server
    service mysql start
    mysql_secure_installation
    mysql
    
    SHOW VARIABLES LIKE 'lower_case_%';
    exit
    ```


##
