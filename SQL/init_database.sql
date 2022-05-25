/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2022/4/27 9:50:37                            */
/*==============================================================*/

drop database IF EXISTS BankApp;
create database BankApp;
use BankApp;


/*==============================================================*/
/* Table: Account                                               */
/*==============================================================*/
/*create table Account
(
    Account_ID      char(32) not null comment '账户号',
    Account_balance float comment '账户余额',
    Reg_Date        date comment '开户日期',
    Reg_Bank        char(32) comment '开户支行',
    primary key (Account_ID)
);*/

/*==============================================================*/
/* Table: CheckAccount                                          */
/*==============================================================*/
create table CheckAccount
(
    Account_ID      char(32) not null comment '支票账户号',
    Account_balance float comment '账户余额',
    Reg_Date        date comment '开户日期',
    Reg_Bank        char(32) comment '开户支行',
    Overdraft       float comment '透支额度',
    primary key (Account_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Customer                                              */
/*==============================================================*/
create table Customer
(
    User_ID                   char(16)  not null comment '客户身份证号码',
    User_Name                 char(32) comment '客户姓名',
    User_PhoneNumber          char(16) comment '客户电话',
    User_Address              char(64) comment '客户家庭地址',
    User_Contacts_Name        char(32) comment '联系人姓名',
    User_Contacts_PhoneNumber char(16) comment '联系人电话',
    User_Contacts_Email       char(32) comment '联系人电子邮件',
    User_Contacts_Relation    char(32) comment '客户与联系人关系',
    User_Username             char(16)  not null comment '员工账户用户名',
    User_Password             char(128) not null comment '员工账户密码',
    primary key (User_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Customer_CheckAccount                                 */
/*==============================================================*/
create table Customer_CheckAccount
(
    User_ID        char(16) not null comment '户主身份证号码',
    Bank_Name      char(32) not null comment '开户支行支行名',
    Account_ID     char(32) not null comment '对应的支票账户账户号',
    Last_View_Date date comment '最近访问日期',
    primary key (User_ID, Bank_Name)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Customer_DepositAccount                               */
/*==============================================================*/
create table Customer_DepositAccount
(
    User_ID        char(16) not null comment '户主身份证号码',
    Bank_Name      char(32) not null comment '开户支行支行名',
    Account_ID     char(32) not null comment '对应的储蓄账户账户号',
    Last_View_Date date comment '最近访问日期',
    primary key (User_ID, Bank_Name)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Customer_Loan                                         */
/*==============================================================*/
create table Customer_Loan
(
    Loan_ID char(16) not null comment '贷款号',
    User_ID char(16) not null comment '用户身份证号码',
    primary key (Loan_ID, User_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Department                                            */
/*==============================================================*/
create table Department
(
    Department_ID         char(32) not null comment '',
    Bank_Name             char(32) not null comment '',
    Department_Name       char(32) comment '',
    Department_Type       char(32) comment '',
    Department_Manager_ID char(16) not null comment '',
    primary key (Department_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: DepositAccount                                        */
/*==============================================================*/
create table DepositAccount
(
    Account_ID      char(32) not null comment '储蓄账户号',
    Account_balance float comment '账户余额',
    Reg_Date        date comment '开户日期',
    Reg_Bank        char(32) comment '开户行',
    Interest_Rate   float comment '利率',
    Currency_type   tinyint comment '货币类型',
    primary key (Account_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Employee                                              */
/*==============================================================*/
create table Employee
(
    Employee_ID          char(16)  not null comment '员工身份证号码',
    Department_ID        char(32)  not null comment '员工所在部门ID',
    Employee_Name        char(32) comment '员工姓名',
    Employee_PhoneNumber decimal(12) comment '员工电话',
    Employee_Address     char(64) comment '员工家庭住址',
    Employee_Enter_Date  date comment '员工入职日期',
    Employee_Username    char(16)  not null comment '员工账户用户名',
    Employee_Password    char(128) not null comment '员工账户密码',
    Is_Manager           tinyint   not null comment '经理标识',
    primary key (Employee_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Employee_Customer                                     */
/*==============================================================*/
create table Employee_Customer
(
    Employee_ID  char(16) not null comment '员工身份证号码',
    User_ID      char(16) not null comment '用户身份证号码',
    Service_Type char(32) comment '服务类型',
    primary key (Employee_ID, User_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Loan                                                  */
/*==============================================================*/
create table Loan
(
    Loan_ID     char(16) not null comment '贷款号',
    Bank_Name   char(32) not null comment '发放支行名',
    Loan_Money  float comment '贷款额度',
    Loan_Status tinyint DEFAULT 0 comment '发放状态',
    primary key (Loan_ID)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: Payment                                               */
/*==============================================================*/
create table Payment
(
    Loan_ID   char(16) not null comment '支付对应的贷款号',
    Pay_Date  date comment '支付日期',
    Pay_Money float comment '支付金额',
    primary key (Loan_ID, Pay_Date)
)DEFAULT CHARSET=utf8;

/*==============================================================*/
/* Table: SubBank                                               */
/*==============================================================*/
create table SubBank
(
    Bank_Name     char(32) not null comment '支行名称',
    Bank_City     char(32) comment '支行所在城市',
    Bank_Property float DEFAULT 0.0 comment '支行资产',
    primary key (Bank_Name)
)DEFAULT CHARSET=utf8;

/*alter table CheckAccount
    add constraint FK_CHECKACC_ACCOUNT_C_ACCOUNT foreign key (Account_ID)
        references Account (Account_ID);*/

alter table Customer_CheckAccount
    add constraint FK_CUSTOMER_CHECKACCO_CHECKACC foreign key (Account_ID)
        references CheckAccount (Account_ID) on delete restrict on update restrict;

alter table Customer_CheckAccount
    add constraint FK_CUSTOMER_CUSTOMER__CUSTOMER foreign key (User_ID)
        references Customer (User_ID) on delete restrict on update restrict;

alter table Customer_CheckAccount
    add constraint FK_CUSTOMER_SUBBANK_C_SUBBANK foreign key (Bank_Name)
        references SubBank (Bank_Name) on delete restrict on update restrict;

alter table Customer_DepositAccount
    add constraint FK_CUSTOMER_CUSTOMER__CUSTOMER1 foreign key (User_ID)
        references Customer (User_ID) on delete restrict on update restrict;

alter table Customer_DepositAccount
    add constraint FK_CUSTOMER_DEPOSITAC_DEPOSITA foreign key (Account_ID)
        references DepositAccount (Account_ID) on delete restrict on update restrict;

alter table Customer_DepositAccount
    add constraint FK_CUSTOMER_SUBBANK_D_SUBBANK foreign key (Bank_Name)
        references SubBank (Bank_Name) on delete restrict on update restrict;

alter table Customer_Loan
    add constraint FK_CUSTOMER_CUSTOMER__LOAN foreign key (Loan_ID)
        references Loan (Loan_ID) on delete restrict on update restrict;

alter table Customer_Loan
    add constraint FK_CUSTOMER_CUSTOMER__CUSTOMER2 foreign key (User_ID)
        references Customer (User_ID) on delete restrict on update restrict;

alter table Department
    add constraint FK_DEPARTME_SUBBANK_D_SUBBANK foreign key (Bank_Name)
        references SubBank (Bank_Name) on delete restrict on update restrict;

/*alter table DepositAccount
    add constraint FK_DEPOSITA_ACCOUNT_D_ACCOUNT foreign key (Account_ID)
        references Account (Account_ID) on delete restrict on update restrict;*/

alter table Employee
    add constraint FK_EMPLOYEE_EMPLOYEE__DEPARTME foreign key (Department_ID)
        references Department (Department_ID) on delete restrict on update restrict;

alter table Employee_Customer
    add constraint FK_EMPLOYEE_EMPLOYEE__EMPLOYEE foreign key (Employee_ID)
        references Employee (Employee_ID) on delete restrict on update restrict;

alter table Employee_Customer
    add constraint FK_EMPLOYEE_EMPLOYEE__CUSTOMER foreign key (User_ID)
        references Customer (User_ID) on delete restrict on update restrict;

alter table Loan
    add constraint FK_LOAN_LOAN_SUBB_SUBBANK foreign key (Bank_Name)
        references SubBank (Bank_Name) on delete restrict on update restrict;

alter table Payment
    add constraint FK_PAYMENT_PAY_LOAN_LOAN foreign key (Loan_ID)
        references Loan (Loan_ID) on delete restrict on update restrict;
