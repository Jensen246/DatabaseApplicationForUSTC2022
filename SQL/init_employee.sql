use BankApp;
delete
from Employee
where Employee_ID is not NULL;
# 员工初始化
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00001", "张三", "120418", "合肥西路38号", "2000/12/5", "01", 1, "zhangsan", "zhangsan");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00002", "李四", "195182", "合肥南路60号", "2012/5/23", "02", 1, "lisi", "lisi");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00007", "王五", "102321", "合肥东路12号", "2012/5/23", "02", 0, "wangwu", "wangwu");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00003", "小明", "684930", "合肥北路20号", "2010/3/12", "01", 1, "xiaoming", "xiaoming");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00008", "小强", "656306", "合肥火车站20号", "2019/4/4", "01", 0, "xiaoqiang", "xiaoqiang");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00004", "小李", "698203", "合肥广场31号", "2009/11/12", "02", 1, "xiaoli", "xiaoli");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00005", "大牛", "799103", "上海大厦3栋", "2009/11/12", "01", 1, "daniu", "daniu");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00006", "James", "745443", "上海红星1号", "2001/1/12", "02", 1, "james", "james");
insert into Employee(Employee_ID, Employee_Name, Employee_PhoneNumber, Employee_Address, Employee_Enter_Date,
                     Department_ID, Is_Manager, Employee_Username, Employee_Password)
values ("00009", "Hades", "787771", "上海红星1号", "1999/10/2", "02", 0, "hades", "hades");
select *
from Employee;