import sys
import cx_Oracle
from datetime import date, timedelta

dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='orcl')
con = cx_Oracle.connect("cisadm", "cisadm", dsn)

today = date.today()


def getAccountsToProcessOne(cycCode):
    cur = con.cursor()

    sql_selectAcct = """
        select ACCT_ID from HS_CI_ACCT where BILL_CYC_CD = :cycCode and BILL_AFTER_DT <= :today
        """

    cur.execute(sql_selectAcct, [cycCode, today])
    cycAccounts = []
    for row in cur:
        cycAccounts.append(row)

    cur.close()

    accountsToProcess = [x[0] for x in cycAccounts]
    return accountsToProcess

    return billEndDates


def getAccountsToProcessTwo(cycCode):
    cur = con.cursor()

    sql_selectAcct = """
        select ACCT_ID from HS_CI_ACCT where BILL_CYC_CD = :cycCode and BILL_AFTER_DT <= :today
        """

    cur.execute(sql_selectAcct, [cycCode, today])
    cycAccounts = cur.fetchall()

    cur.close()
    accountsToProcess = [x[0] for x in cycAccounts]
    return accountsToProcess


def getAccountsToProcessThree(cycCode):
    cur = con.cursor()

    sql_selectAcct = """
        select ACCT_ID from HS_CI_ACCT where BILL_CYC_CD = :cycCode and BILL_AFTER_DT <= :today
        """

    cur.execute(sql_selectAcct, [cycCode, today])
    while True:
        cycAccounts = cur.fetchmany(numRows=10)
        if not cycAccounts:
            break

    cur.close()
    accountsToProcess = [x[0] for x in cycAccounts]
    return accountsToProcess


def getAccountsToProcessFour(cycCode):
    cur = con.cursor()

    sql_selectAcct = """
        select ACCT_ID from HS_CI_ACCT where BILL_CYC_CD = :cycCode and BILL_AFTER_DT <= :today
        """

    cur.execute(sql_selectAcct, [cycCode, today])
    while True:
        cycAccounts = cur.fetchone()
        if cycAccounts is None:
            break

    cur.close()
    accountsToProcess = [x[0] for x in cycAccounts]
    return accountsToProcess


def getAccountsToProcessFive(cycCode):
    cur = con.cursor()

    accToProcessBind = cur.var(str)
    plsql_selectAcct = (
        'begin '
        'select ACCT_ID into :accToProcessBind '
        'from HS_CI_ACCT where BILL_CYC_CD = :cycCode and BILL_AFTER_DT <= :today '
        'end; ')

    cur.execute(plsql_selectAcct, accToProcessBind=accToProcessBind, cycCode=cycCode, today=today)
    accountsToProcess = accToProcessBind.getValue();

    cur.close()
    return accountsToProcess
