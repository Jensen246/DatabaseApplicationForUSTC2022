# 客户以及账户初始化
use BankApp;

SET FOREIGN_KEY_CHECKS = 0;

delete
from Customer_CheckAccount
where Account_ID is not NULL;

delete
from Customer_DepositAccount
where Account_ID is not NULL;

delete
from CheckAccount
where Account_ID is not NULL;

delete
from DepositAccount
where Account_ID is not NULL;

delete
from Customer
where User_ID is not NULL;

/*
delete
from Account
where Account_ID is not null;
*/

SET FOREIGN_KEY_CHECKS = 1;


insert into Customer value ("10294", "王大海", "423890", "合肥蜀山区黄山南路10号", "王小河", "423891", "xiaohe@163.com", "父子", "dahai",
                            "dahai");
insert into Customer value ("10188", "齐秦", "124090", "上海浦东新区红星小区2栋207", "齐天赐", "124091", "qtc@foxmail.com", "母女",
                            "qiqin", "qiqin");
insert into Customer value ("21233", "Is'ral", "787712", "Shanghai Hongxing Dist. 711", "O'neil", "787713",
                            "oneil@gmail.com", "夫妻", "isral", "isral");
select *
from Customer;

/*
insert into Account value ("001", 0, "2008/12/30", "合肥西支行");
insert into Account value ("002", 0, "2009/2/3", "合肥东支行");
insert into Account value ("003", 0, "2010/11/4", "上海总部");
*/

insert into DepositAccount value ("dp1", 30000, "2018/12/30", "合肥西支行", "0.035", 0);
insert into Customer_DepositAccount value ("10188", "合肥西支行", "dp1", "2022/5/20");
insert into Customer_DepositAccount value ("10294", "合肥西支行", "dp1", "2022/5/07");

insert into DepositAccount value ("dp2", 40000, "2019/2/3", "合肥东支行", "0.03", 3);
insert into DepositAccount value ("dp3", 20000, "2020/11/4", "上海总部", "0.05", 1);
insert into Customer_DepositAccount value ("10294", "合肥东支行", "dp2", "2022/4/6");
insert into Customer_DepositAccount value ("10294", "上海总部", "dp3", "2022/2/24");



insert into CheckAccount value ("ck1", 20000, "2018/12/30", "合肥西支行", 50000);
insert into Customer_CheckAccount value ("10188", "合肥西支行", "ck1", "2022/1/27");

insert into CheckAccount value ("ck2", 70000, "2019/2/3", "合肥东支行", 50000);
insert into CheckAccount value ("ck3", 40000, "2020/11/4", "上海总部", 10000);
insert into Customer_CheckAccount value ("10294", "合肥东支行", "ck2", "2022/4/20");
insert into Customer_CheckAccount value ("10294", "上海总部", "ck3", "2022/2/22");