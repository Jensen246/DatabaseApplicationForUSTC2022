# 贷款初始化

delete from customer_loan where User_ID is not NULL;
delete from payment where Loan_ID is not NULL;
delete from loan where Loan_ID is not NULL;

insert into Loan value("ln1","合肥西支行",320000,2);
insert into Loan value("ln2","合肥西支行",120000,0);
insert into Loan value("ln3","合肥东支行",440000,0);
insert into Loan value("ln4","上海总部",770000,1);

insert into customer_loan value("ln1","10294");
insert into customer_loan value("ln3","10294");
insert into customer_loan value("ln4","10188");
insert into customer_loan value("ln2","10188");
insert into customer_loan value("ln2","10294");

insert into payment value("ln1","2019/6/16",200000);
insert into payment value("ln1","2020/6/16",120000);
insert into payment value("ln4","2021/8/21",350000);