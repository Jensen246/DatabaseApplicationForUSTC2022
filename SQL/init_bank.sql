use BankApp;

delete
from SubBank
where Bank_City is not NULL;
delete
from Department
where Department_ID is not NULL;

# 银行初始化
insert into SubBank(Bank_City, Bank_Name)
values ("合肥", "合肥西支行");
insert into SubBank(Bank_City, Bank_Name)
values ("合肥", "合肥东支行");
insert into SubBank(Bank_City, Bank_Name)
values ("上海", "上海总部");
select *
from SubBank;
# 部门初始化
insert into Department(Department_ID, Department_Name, Department_Type, Department_Manager_ID, Bank_name)
values ("01", "营销部", "loan", "00001", "合肥西支行");
insert into Department(Department_ID, Department_Name, Department_Type, Department_Manager_ID, Bank_name)
values ("02", "客服部", "service", "00002", "合肥西支行");
insert into Department(Department_ID, Department_Name, Department_Type, Department_Manager_ID, Bank_name)
values ("01", "营销部", "loan", "00003", "合肥东支行");
insert into Department(Department_ID, Department_Name, Department_Type, Department_Manager_ID, Bank_name)
values ("02", "客服部", "service", "00004", "合肥东支行");
insert into Department(Department_ID, Department_Name, Department_Type, Department_Manager_ID, Bank_name)
values ("01", "营销部", "loan", "00005", "上海总部");
insert into Department(Department_ID, Department_Name, Department_Type, Department_Manager_ID, Bank_name)
values ("02", "客服部", "service", "00006", "上海总部");
select *
from Department;
