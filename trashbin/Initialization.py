from trashbin.ExecSql import Execute_File, Execute_Sentence

Execute_Sentence("drop database IF EXISTS BankApp")
Execute_Sentence("create database BankApp;")
Execute_File("../SQL/init_database.sql", 1)

Execute_File("../SQL/init_bank.sql", 1)

# Execute_File("SQL/init_employee.sql", 0)
