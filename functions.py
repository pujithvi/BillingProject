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


# Program C - Retrieve the end dates of the bills associated with an account
# this program could be replaced with a program that gets the bill history of an account later, and then have a method here to get the end dates
def retrieveBillEndDates(account):
    cur = con.cursor()
    #billEndDates = ""

    sql_retrieveBillHistory = """
            select END_DT from HS_CI_BILL where ACCT_ID = :account
            """

    billEndDates = []
    cur.execute(sql_retrieveBillHistory, [account])
    for row in cur:
        billEndDates.append(row)

    cur.close()

    return billEndDates


# Program D - Find the most recent end date of the account
def findMostRecentEndDate(billEndDates):
    mostRecentDate = ""
    diff = sys.maxsize
    for endDate in billEndDates:
        endDate = endDate[0]
        if (today - endDate.date()).days < diff:
            diff = (today - endDate.date()).days
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


# May need to modify if one account can have multiple meters


# Gets SA corresponding to account
def getSA(account):
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

    cur.close()

    return serviceAgreementID


# Gets SP corresponding to SA
def getSP(serviceAgreementID):
    cur = con.cursor()
    servicePointIDBind = cur.var(str)

    plsql_selectSP_ID = (
        'begin'
        'select SP_ID into :servicePointIDBind'
        'from HS_CI_SA_SP where SA_ID = :serviceAgreementIDBind'
        'end'
    )

    cur.execute(plsql_selectSP_ID, servicePointIDBind=servicePointIDBind,
                serviceAgreementIDBind=serviceAgreementID)
    servicePointID = servicePointIDBind.getValue()

    cur.close()

    return servicePointID


# Gets ID of meter corresponding to SP
def getMeter(servicePointID):
    cur = con.cursor()
    meterConfigIDBind = cur.var(str)

    plsql_selectMTR_CONFIG_ID = (
        'begin'
        'select MTR_CONFIG_ID into :meterConfigIDBind'
        'from HS_CI_SP where SP_ID = :servicePointIDBind'
        'end'
    )

    cur.execute(plsql_selectMTR_CONFIG_ID, meterConfigIDBind=meterConfigIDBind,
                servicePointIDBind=servicePointID)
    meterConfigID = meterConfigIDBind.getValue()

    cur.close()

    return meterConfigID

    # Experimental join statement
    # sql_join = """
    # select HS_CI_SP.MTR_CONFIG_ID from HS_CI_ACCT join HS_CI_SA on HS_CI_ACCT.ACCT_ID = HS_CI_SA.ACCT_ID join HS_CI_SA_SP on HS_CI_SA_SP.SA_ID = HS_CI_SA.SA_ID join HS_CI_SP on HS_CI_SP.SP_ID = HS_CI_SA_SP.SP_ID join HS_CI_MR on HS_CI_MR.MTR_CONFIG_ID = HS_CI_SP.MTR_CONFIG_IG where HS_CI_ACCT.ACCT_ID = :account
    # """

    # cur.execute(sql_join, account = account)
    # meterConfigID = cur.fetchall()


def getGasUsage(meterConfigID, startDate):
    cur = con.cursor()

    InitialReadBind = cur.var(int)

    plsql_retrieveInitialRead = (
        'begin'
        'select top 1 REG_READING into :InitialReadBind'
        'from HS_CI_MR where MTR_CONFIG_ID = :meterConfigID and READ_DTTM >= :startDate and READ_TYPE_FLG != \'20\''
        'order by READ_DTTM asc'
        'end'
    )

    cur.execute(plsql_retrieveInitialRead,
                InitialReadBind=InitialReadBind, meterConfigID=meterConfigID, startDate=startDate)
    initialReading = InitialReadBind.getValue()

    FinalReadBind = cur.var(int)

    plsql_retrieveFinalRead = (
        'begin'
        'select top 1 REG_READING into :FinalReadBind'
        'from HS_CI_MR where MTR_CONFIG_ID = :meterConfigID and READ_DTTM >= :startDate and READ_TYPE_FLG != \'20\''
        'order by READ_DTTM desc'
        'end'
    )

    cur.execute(plsql_retrieveFinalRead,
                FinalReadBind=FinalReadBind, meterConfigID=meterConfigID, startDate=startDate)
    finalReading = FinalReadBind.getValue()

    cur.close()

    return finalReading - initialReading


def convertToTherms(usage):
    return usage / 1.037


# Method for billing
# May need to split up into multiple methods
# could split up into two methods: charge usage and add AGL cost
# also, a join between SA and RS tables might be useful

def getTotalCost(account, usage):
    cur = con.cursor()

    SARateScheduleCodeBind = cur.var(str)

    serviceAgreementID = getSA(account)

    pl_sql_retrieveSARateScheduleCode = (
        'begin'
        'select RS_CD into :SARateScheduleCodeBind'
        'from HS_CI_SA where SA_ID = :serviceAgreementID'
        'end'
    )

    cur.execute(pl_sql_retrieveSARateScheduleCode,
                SARateScheduleCodeBind=SARateScheduleCodeBind, serviceAgreementID=serviceAgreementID)
    SARateScheduleCode = SARateScheduleCodeBind.getValue()

    AGLChargeBind = cur.var(int)

    pl_sql_retrieveAGLCharge = (
        'begin'
        'select FIXED_CHG, RS_CD into :AGLChargeBind'
        'from HS_CI_RS where :SARateScheduleCode in SA_TYPE_CD and HEADER_SEQ = 1 and SEQ_NO = 1'
        'end'
    )

    cur.execute(pl_sql_retrieveAGLCharge,
                AGLChargeBind=AGLChargeBind, SARateScheduleCode=SARateScheduleCode)

    AGLCharge = AGLChargeBind.getValue()

    if 'RES' in SARateScheduleCode:

        stepRateBind = cur.var(int)

        pl_sql_retrieveBillingRate = (
            'begin'
            'select STEP_RATE into :stepRateBind'
            'from HS_CI_RS where RS_CD = :SARateScheduleCode and HEADER_SEQ = 2'
            'end'
        )

        cur.execute(pl_sql_retrieveBillingRate,
                    stepRateBind=stepRateBind, SARateScheduleCode=SARateScheduleCode)
        stepRate = stepRateBind.getValue()

        usageCost = usage * stepRate

    elif 'COM' in SARateScheduleCode:

        stepRateBind = cur.var(int)
        lowerLimitBind = cur.var(int)
        upperLimitBind = cur.var(int)

        usageCost = 0
        seqNo = 1

        while upperLimit != 99999999.99:
            # might be better to have this query outside the while loop and include some different logic
            # as that would reduce round trips
            pl_sql_retrieveBillingRate = (
                'begin'
                'select STEP_RATE, STEP_LOW_LMT, STEP_HIGH_LMT into :stepRateBind, :lowerLimitBind, :upperLimitBind'
                'from HS_CI_RS where RS_CD = :RSCode and HEADER_SEQ = 2 and SEQ_NO = :seqNo'
                'end'
            )

            cur.execute(pl_sql_retrieveBillingRate, stepRateBind=stepRateBind,
                        lowerLimitBind=lowerLimitBind, upperLimitBind=upperLimitBind, RSCode=RSCode, seqNo=seqNo)

            stepRate = stepRateBind.getValue()
            lowerLimit = lowerLimitBind.getValue()
            upperLimit = upperLimitBind.getValue()

            if usage < upperLimit-lowerLimit:
                usageCost += usage * stepRate
                break

            else:
                usageCost += upperLimit-lowerLimit * stepRate

            usage = usage - upperLimit

            seqNo += 1

    return usageCost + AGLCharge
