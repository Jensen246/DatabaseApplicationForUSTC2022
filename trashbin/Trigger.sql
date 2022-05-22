use BankApp;
drop trigger IF EXISTS UpdateAccountBalance_deposit_update_before;
drop trigger IF EXISTS UpdateAccountBalance_deposit_update_after;
drop trigger IF EXISTS UpdateAccountBalance_check_update_before;
drop trigger IF EXISTS UpdateAccountBalance_check_update_after;
drop trigger IF EXISTS UpdateAccountBalance_deposit_insert;
drop trigger IF EXISTS UpdateAccountBalance_check_insert;
drop trigger IF EXISTS UpdateAccountBalance_deposit_delete;
drop trigger IF EXISTS UpdateAccountBalance_check_delete;

# 触发器
Delimiter //
# 储蓄账户更新
Create Trigger UpdateAccountBalance_deposit_update_before
    Before update
    On DepositAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance - depositaccount.Account_balance
    where Account.Account_ID = depositaccount.Account_ID;
End;

Create Trigger UpdateAccountBalance_deposit_update_after
    After update
    On DepositAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance + DepositAccount.Account_balance
    where Account.Account_ID = DepositAccount.Account_ID;
End;
# 支票账户更新
Create Trigger UpdateAccountBalance_check_update_before
    Before update
    On CheckAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance - CheckAccount.Account_balance
    where Account.Account_ID = CheckAccount.Account_ID;
End;

Create Trigger UpdateAccountBalance_check_update_after
    After update
    On CheckAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance + CheckAccount.Account_balance
    where Account.Account_ID = CheckAccount.Account_ID;
End;

# 储蓄账户插入
Create Trigger UpdateAccountBalance_deposit_insert
    After insert
    On DepositAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance + DepositAccount.Account_balance
    where Account.Account_ID = DepositAccount.Account_ID;
End;

# 支票账户插入
Create Trigger UpdateAccountBalance_check_insert
    After insert
    On CheckAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance + CheckAccount.Account_balance
    where Account.Account_ID = CheckAccount.Account_ID;
End;

# 储蓄账户删除
Create Trigger UpdateAccountBalance_deposit_delete
    Before delete
    On DepositAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance - DepositAccount.Account_balance
    where Account.Account_ID = DepositAccount.Account_ID;
End;

# 支票账户删除
Create Trigger UpdateAccountBalance_check_delete
    Before delete
    On CheckAccount
    For Each Row

Begin
    Update Account
    Set Account_balance = Account_balance - CheckAccount.Account_balance
    where Account.Account_ID = CheckAccount.Account_ID;
End;
//
Delimiter ;