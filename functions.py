import sys
import cx_Oracle
from datetime import date, timedelta

dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='orcl')
con = cx_Oracle.connect("cisadm", "cisadm", dsn)

today = date.today()


# PROGRAM A - Retrieve the current bill cycle


def getCycCode():
    cur = con.cursor()
    cycCodeBind = cur.var(str)

    plsql_selectBillSch = (
        'begin '
        'select BILL_CYC_CD into :cycCodeBind '
        'from HS_CI_BILL_CYC_SCH where WIN_START_DT <= :today and WIN_END_DT >= :today; '
        'end; ')

    cur.execute(plsql_selectBillSch, cycCodeBind=cycCodeBind, today=today)
    cycCode = cycCodeBind.getvalue()

    cur.close()
    return cycCode


# Program B - Retrieve a list of accounts to process


def getAccountsToProcess(cycCode):
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


# Program C - Retrieve the bill history of the account


def retrieveBillHistory(account):
    cur = con.cursor()
    billEndDateBind = cur.var(date)

    plsql_retrieveBillHistory = (
        'begin '
        'select END_DT into :billEndDateBind '
        'from HS_CI_BILL where ACCT_ID = :account '
        'end; ')

    cur.execute(plsql_retrieveBillHistory,
                billEndDateBind=billEndDateBind, account=account)
    billEndDates = billEndDateBind.getValue()

    cur.close()

    return billEndDates


# Program D - Find the most recent bill of the account


def findMostRecentBill(billEndDates):
    mostRecentDate = ""
    diff = sys.maxsize
    for endDate in billEndDates:
        if (today - endDate).days < diff:
            diff = (today - endDate).days
            mostRecentDate = endDate

    return mostRecentDate


# Program E - Create a default start date


def createStartDate(mostRecentDate, account):
    cur = con.cursor()
    defaultStartDateBind = cur.var(date)

    plsql_retrieveDefaultStartDate = (
        'begin '
        'select START_DT into :defaultStartDateBind '
        'from HS_CI_ACCT where ACCT_ID = :account '
        'end; '
    )

    cur.execute(plsql_retrieveDefaultStartDate,
                defaultStartDateBind=defaultStartDateBind, account=account)
    defaultStartDate = defaultStartDateBind.getValue()

    cur.close()

    if mostRecentDate == "":
        startDate = defaultStartDate
    else:
        startDate = mostRecentDate + timedelta(days=1)

    return startDate


def getMeter(account):
    cur = con.cursor()
    serviceAgreementIDBind = cur.var(str)

    plsql_selectSA_ID = (
        'begin'
        'select SA_ID into :serviceAgreementIDBind'
        'from HS_CI_SA where ACCT_ID = :account'
        'end'
    )

    cur.execute(plsql_selectSA_ID,
                serviceAgreementIDBind=serviceAgreementIDBind, account=account)

    serviceAgreementID = serviceAgreementIDBind.getValue()

    servicePointIDBind = cur.var(str)

    plsql_selectSP_ID = (
        'begin'
        'select SP_ID into :servicePointIDBind'
        'from HS_CI_SA_SP where SA_ID = :serviceAgreementIDBind2'
        'end'
    )

    cur.execute(plsql_selectSP_ID, servicePointIDBind=servicePointIDBind,
                serviceAgreementIDBind2=serviceAgreementID)

    servicePointID = servicePointIDBind.getValue()

    meterConfigIDBind = cur.var(str)

    plsql_selectMTR_CONFIG_ID = (
        'begin'
        'select MTR_CONFIG_ID into :meterConfigIDBind'
        'from HS_CI_SP where SP_ID = :servicePointIDBind2'
        'end'
    )

    cur.execute(plsql_selectMTR_CONFIG_ID, meterConfigIDBind=meterConfigIDBind,
                servicePointIDBind2=servicePointID)

    meterConfigID = meterConfigIDBind.getValue()

    # Experimental join statement
    # sql_join = """
    # select HS_CI_SP.MTR_CONFIG_ID from HS_CI_ACCT join HS_CI_SA on HS_CI_ACCT.ACCT_ID = HS_CI_SA.ACCT_ID join HS_CI_SA_SP on HS_CI_SA_SP.SA_ID = HS_CI_SA.SA_ID join HS_CI_SP on HS_CI_SP.SP_ID = HS_CI_SA_SP.SP_ID join HS_CI_MR on HS_CI_MR.MTR_CONFIG_ID = HS_CI_SP.MTR_CONFIG_IG where HS_CI_ACCT.ACCT_ID = :account
    # """

    # cur.execute(sql_join, account = account)
    # meterConfigID = cur.fetchall()

    return meterConfigID


def getGasUsage(meterConfigID, startDate):
    cur = con.cursor()

    InitialReadBind = cur.var(int)

    plsql_retrieveInitialRead = (
        'begin'
        'select REG_READING into :InitialReadBind'
        # Don't think 'READ_DTTM = :startDate' is right
        'from HS_CI_MR where MTR_CONFIG_ID = :meterConfigID and READ_DTTM = :startDate'
    )

    cur.execute(plsql_retrieveInitialRead,
                InitialReadBind=InitialReadBind, startDate=startDate)

    initialReading = InitialReadBind.getValue()

    FinalReadBind = cur.var(int)

    plsql_retrieveFinalRead = (
        'begin'
        'select REG_READING into :FinalReadBind'
        # Don't think 'READ_DTTM = :startDate' is right
        'from HS_CI_MR where MTR_CONFIG_ID = :meterConfigID and READ_DTTM = :endDate'
    )

    # What is the endDate? It's not today's date I think
    cur.execute(plsql_retrieveFinalRead,
                FinalReadBind=FinalReadBind, endDate=date.today())

    finalReading = FinalReadBind.getValue()

    return finalReading - initialReading
