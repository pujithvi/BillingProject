import sys
import cx_Oracle
import os
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
        'select SETUP_DT into :defaultStartDateBind '
        'from HS_CI_ACCT where ACCT_ID = :account; '
        'end; '
    )

    cur.execute(plsql_retrieveDefaultStartDate,
                defaultStartDateBind=defaultStartDateBind, account=account)

    defaultStartDate = defaultStartDateBind.getvalue()

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
        'begin '
        'select SA_ID into :serviceAgreementIDBind '
        'from HS_CI_SA where ACCT_ID = :account; '
        'end; ')

    cur.execute(plsql_selectSA_ID,
                serviceAgreementIDBind=serviceAgreementIDBind, account=account)

    serviceAgreementID = serviceAgreementIDBind.getvalue()

    cur.close()

    return serviceAgreementID


# Gets SP corresponding to SA
def getSP(serviceAgreementID):
    cur = con.cursor()
    servicePointIDBind = cur.var(str)

    plsql_selectSP_ID = (
        'begin '
        'select SP_ID into :servicePointIDBind '
        'from HS_CI_SA_SP where SA_ID = :serviceAgreementIDBind; '
        'end; '
    )

    cur.execute(plsql_selectSP_ID, servicePointIDBind=servicePointIDBind,
                serviceAgreementIDBind=serviceAgreementID)

    servicePointID = servicePointIDBind.getvalue()

    cur.close()

    return servicePointID


# Gets ID of meter corresponding to SP
def getMeter(servicePointID):
    cur = con.cursor()
    meterConfigIDBind = cur.var(str)

    plsql_selectMTR_CONFIG_ID = (
        'begin '
        'select MTR_CONFIG_ID into :meterConfigIDBind '
        'from HS_CI_SP where SP_ID = :servicePointIDBind; '
        'end; '
    )

    cur.execute(plsql_selectMTR_CONFIG_ID, meterConfigIDBind=meterConfigIDBind,
                servicePointIDBind=servicePointID)
    meterConfigID = meterConfigIDBind.getvalue()

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

    sql_retrieveInitialRead = """select REG_READING, READ_DTTM from HS_CI_MR where MTR_CONFIG_ID = :meterConfigID and READ_TYPE_FLG != \'20\' and READ_TYPE_FLG != \'30\' order by READ_DTTM asc """

    startDate = startDate.date()
    cur.execute(sql_retrieveInitialRead,
                meterConfigID=meterConfigID)

    initialReading, initialDate = cur.fetchone()

    plsql_retrieveInitialRead = (
        'begin '
        'select REG_READING '
        'into :InitialReadBind '
        'from HS_CI_MR '
        'where MTR_CONFIG_ID = :meterConfigID '
        'and READ_TYPE_FLG != \'20\' '
        'order by READ_DTTM asc; '
        'end; ')

    # cur.execute(plsql_retrieveInitialRead,
    # InitialReadBind=InitialReadBind, meterConfigID=meterConfigID)
    # initialReading = InitialReadBind.getvalue()

    FinalReadBind = cur.var(int)

    sql_retrieveFinalRead = """select REG_READING, READ_DTTM from HS_CI_MR where MTR_CONFIG_ID = :meterConfigID and READ_TYPE_FLG != \'20\' and READ_TYPE_FLG != \'30\' and REG_READING != :initialReading order by READ_DTTM asc """
    # (temporary) fix for monthly gas usage

    cur.execute(sql_retrieveFinalRead, meterConfigID=meterConfigID,
                initialReading=initialReading)

    finalReading, finalDate = cur.fetchone()

    #print('final reading: ', finalReading)

    plsql_retrieveFinalRead = (
        'begin '
        'select top 1 REG_READING into :FinalReadBind '
        'from HS_CI_MR where MTR_CONFIG_ID = :meterConfigID and READ_DTTM >= :startDate and READ_TYPE_FLG != \'20\'; '
        'order by READ_DTTM desc '
        'end; '
    )

    # cur.execute(plsql_retrieveFinalRead,
    # FinalReadBind=FinalReadBind, meterConfigID=meterConfigID, startDate=startDate)
    #finalReading = FinalReadBind.getvalue()

    cur.close()

    return [initialDate, finalDate, finalReading - initialReading]


def convertToTherms(usage):
    return usage / 1.037


# Methods for billing
# May need to split up into multiple methods
# could split up into two methods: charge usage and add AGL cost
# also, a join between SA and RS tables might be useful


def getRateSchedule(account):
    cur = con.cursor()

    SARateScheduleCodeBind = cur.var(str)

    serviceAgreementID = getSA(account)

    pl_sql_retrieveSARateScheduleCode = (
        'begin '
        'select RS_CD into :SARateScheduleCodeBind '
        'from HS_CI_SA where SA_ID = :serviceAgreementID; '
        'end; '
    )

    cur.execute(pl_sql_retrieveSARateScheduleCode,
                SARateScheduleCodeBind=SARateScheduleCodeBind, serviceAgreementID=serviceAgreementID)
    SARateScheduleCode = SARateScheduleCodeBind.getvalue()

    cur.close()
    return SARateScheduleCode


def getAGLFixedCharge(SARateScheduleCode, dictionary):
    try:
        return dictionary[SARateScheduleCode]
    except KeyError:

        cur = con.cursor()

        AGLChargeBind = cur.var(int)

        pl_sql_retrieveAGLCharge = (
            'begin '
            'select FIXED_CHG into :AGLChargeBind '
            'from HS_CI_RS where RS_CD = :SARateScheduleCode and HEADER_SEQ = 1 and SEQ_NO = 1; '
            'end; '
        )

        cur.execute(pl_sql_retrieveAGLCharge,
                    AGLChargeBind=AGLChargeBind, SARateScheduleCode=SARateScheduleCode)
        # No data found error--fixed

        AGLCharge = AGLChargeBind.getvalue()

        cur.close()

        dictionary[SARateScheduleCode] = AGLCharge

        return AGLCharge


def calculateGasCharge(SARateScheduleCode, usage, dictionary):
    cur = con.cursor()

    if 'RES' in SARateScheduleCode:
        try:
            stepRate = dictionary[SARateScheduleCode]
        except KeyError:
            stepRateBind = cur.var(int)

            pl_sql_retrieveBillingRate = (
                'begin '
                'select STEP_RATE into :stepRateBind '
                'from HS_CI_RS where RS_CD = :SARateScheduleCode and HEADER_SEQ = 2; '
                'end; '
            )

            cur.execute(pl_sql_retrieveBillingRate,
                        stepRateBind=stepRateBind, SARateScheduleCode=SARateScheduleCode)
            stepRate = stepRateBind.getvalue()
            dictionary[SARateScheduleCode] = stepRate

        usageCost = usage * stepRate

    elif 'COM' in SARateScheduleCode:

        stepRateBind = cur.var(int)
        lowerLimitBind = cur.var(int)
        upperLimitBind = cur.var(int)
        upperLimit = 0
        usageCost = 0
        seqNo = 1

        while upperLimit != 99999999.99:
            # might be better to have this query outside the while loop and include some different logic
            # as that would reduce round trips
            pl_sql_retrieveBillingRate = (
                'begin '
                'select STEP_RATE, STEP_LOW_LMT, STEP_HIGH_LMT into :stepRateBind, :lowerLimitBind, :upperLimitBind '
                'from HS_CI_RS where RS_CD = :SARateScheduleCode and HEADER_SEQ = 2 and SEQ_NO = :seqNo; '
                'end; '
            )

            cur.execute(pl_sql_retrieveBillingRate, stepRateBind=stepRateBind,
                        lowerLimitBind=lowerLimitBind, upperLimitBind=upperLimitBind, SARateScheduleCode=SARateScheduleCode, seqNo=seqNo)

            stepRate = stepRateBind.getvalue()
            lowerLimit = lowerLimitBind.getvalue()
            upperLimit = upperLimitBind.getvalue()

            difference = upperLimit-lowerLimit

            if usage < difference:
                usageCost += usage * stepRate
                break
            else:
                usageCost += difference * stepRate

            usage = usage - difference

            seqNo += 1

    cur.close()
    return usageCost


# Method for outputting total bill
# Preliminary Attempt
# def billOutput(account='', initialDate='', finalDate='', gasUsage='', AGLCharge='', usageCharge='', fail=False, text = "", path=""):
    
#     os.chdir(path)

#     with open(account + str(initialDate).split(' ')[0] + "Bill.txt", 'w') as file:
#         if account != '':
#             print("Account: " + account, file=file)
#         if initialDate != '' and finalDate != '':
#             print("Billing Period: " + str(initialDate).split(' ')[0] + ' to ' + str(finalDate).split(' ')[0], file=file)
#         if AGLCharge != '':
#             print("AGL Fixed Charge: " + str(AGLCharge), file=file)
#         if gasUsage != '':
#             print('Total Gas Usage (Therms): ' + str(gasUsage), file=file)
#         if usageCharge != '':
#             print("Gas Usage Charge: " + str(usageCharge), file=file)
#         if AGLCharge != '' and usageCharge != '':
#             print("Total Cost: " + str(AGLCharge + usageCharge), file=file)

#         #
#         if fail:
#             print(text, file=file)


#Include below functions as methods inside bill class instead?
def billOutput(bill, fail = False, text = '', path = ''):
    os.chdir(path)
    account = bill.acct_id
    initialDate = bill.start_dt
    finalDate = bill.end_dt
    AGLCharge = bill.agl_charge
    gasUsage = bill.gas_usage
    usageCharge = bill.calc_amt
    billID = bill.bill_id
    billCycCode = bill.bill_cyc_cd
    billDate = bill.bill_dt
    dueDate = bill.due_dt

    with open(account + str(initialDate).split(' ')[0] + "Bill.txt", 'w') as file:
        if billID != None:
            print("Bill ID:", billID, file = file)
        print('Bill Cycle Code:', billCycCode, file=file)
        if account != None:
            print("Account: " + account, file=file)
        if initialDate != None and finalDate != None:
            print("Billing Period: " + str(initialDate).split(' ')[0] + ' to ' + str(finalDate).split(' ')[0], file=file)
        if AGLCharge != None:
            print("AGL Fixed Charge: " + str(AGLCharge), file=file)
        if gasUsage != None:
            print('Total Gas Usage (Therms): ' + str(gasUsage), file=file)
        if usageCharge != None:
            print("Gas Usage Charge: " + str(usageCharge), file=file)
        if AGLCharge != None and usageCharge != None:
            print("Total Cost: " + str(AGLCharge + usageCharge), file=file)
        if billDate != None:
            print('Bill Date:', billDate, file=file)
        if dueDate != None:
            print('Due Date:', dueDate, file=file)

        #
        if fail:
            print(text, file=file)


def addtoBillTable(bill):
    cur = con.cursor()
    sql_insert = '''insert into hs_ci_bill values (:bill_id, :bill_cyc_cd, :start_dt, :end_dt, :acct_id, :bill_dt, :due_dt, :rs_cd, :calc_amt, :descr_on_bill, :exp_msg)'''
    cur.execute(sql_insert, bill_id = bill.bill_id, bill_cyc_cd=bill.bill_cyc_cd, start_dt = bill.start_dt, 
                end_dt = bill.end_dt, acct_id = bill.acct_id, bill_dt = bill.bill_dt, due_dt = bill.due_dt, 
                rs_cd = bill.rs_cd.strip(), calc_amt=bill.calc_amt, descr_on_bill=bill.descr_on_bill, exp_msg = bill.exp_msg)
    con.commit()
    cur.close()
    return
