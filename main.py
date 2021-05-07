from functions import *
from logger import *
from billClass import *
from datetime import date, timedelta
import os
import shutil

AGLCharge_dictionary = {}
Rate_dictionary = {}

dir_path = os.path.dirname(os.path.realpath(__file__))

# create log path
log_path = os.path.join(dir_path, "log")
try:
    shutil.rmtree(log_path)
except OSError as e:
    pass
os.mkdir(log_path)

# create billOutput path
billOutput_path = os.path.join(dir_path, "billOutput")
try:
    shutil.rmtree(billOutput_path)
except OSError as e:
    pass
os.mkdir(billOutput_path)

# print("Directory '% s' created" % log_path)
# print("Directory '% s' created" % billOutput_path)

cycCode = getCycCode()
# print(cycCode)

accountsToProcess = getAccountsToProcess(cycCode)
print(accountsToProcess)

for account in accountsToProcess:

    # print(account)
    l_fileName = '%s\%sLog.txt', log_path, account
    l_fileNameTwo = f'{log_path}\{account}.txt'
    l = setup_logger(account, l_fileNameTwo)

    # Need to do like this for every method (done)
    billEndDates = logThis(l, retrieveBillEndDates, (account,), {})
    if billEndDates is None:
        continue
    # print(billEndDates)

    mostRecentDate = logThis(l, findMostRecentEndDate, (billEndDates,), {})
    if mostRecentDate is None:
        continue
    # print(mostRecentDate)

    startDate = logThis(l, createStartDate, (mostRecentDate, account), {})
    if startDate is None:
        continue
    # print('start date:', startDate)

    serviceAgreement = logThis(l, getSA, (account,), {})
    if serviceAgreement is None:
        bill = Bill(cycCode, acct_id=account, exp_msg="No service agreement for this account.")
        billOutput(bill, fail = True, text="No service agreement for this account.", path=billOutput_path)
        #addtoBillTable(bill)
        #billOutput(account=account, fail=True, text="No service agreement for this account.", path=billOutput_path)
        continue
    # print(serviceAgreement)

    servicePoint = logThis(l, getSP, (serviceAgreement,), {})
    if servicePoint is None:
        bill = Bill(cycCode, acct_id=account, exp_msg='No service point for this account.')
        billOutput(bill, fail =True, text="No service point for this account.", path=billOutput_path)
        #addtoBillTable(bill)
        #billOutput(account=account, fail=True, text="No service point for this account.", path=billOutput_path)
        continue
    # print(servicePoint)

    meter = logThis(l, getMeter, (servicePoint,), {})
    if meter is None:
        bill = Bill(cycCode, acct_id=account, exp_msg="No meter for this account.")
        billOutput(bill, fail = True, text="No meter for this account.", path=billOutput_path)
        #addtoBillTable(bill)
        #billOutput(account=account, fail=True, text="No meter for this account.", path=billOutput_path)
        continue
    # print('meter:', meter)

    initialDate, finalDate, gasUsage = logThis(l, getGasUsage, (meter, startDate), {})
    # if initialDate or finalDate or gasUsage is None:
        # continue
    # problem with the above statement: one of those is returning None
    # print(initialDate)

    gasUsage = logThis(l, convertToTherms, (gasUsage,), {})
    # print(gasUsage)

    rateSchedule = logThis(l, getRateSchedule, (account,), {})
    if rateSchedule is None:
        continue
    #print(rateSchedule)

    AGLCharge = logThis(l, getAGLFixedCharge, (rateSchedule, AGLCharge_dictionary), {})
    if AGLCharge is None:
        continue
    # print(AGLCharge)

    usageCharge = round(logThis(l, calculateGasCharge, (rateSchedule, gasUsage, Rate_dictionary), {}), 2)
    if usageCharge is None:
        continue
    # print(usageCharge)

    gasUsage = round(gasUsage, 2)
    totalCost = round(AGLCharge + usageCharge, 2)
 
    # print(totalCost)
    
    bill = Bill(bill_cyc_cd=cycCode, start_dt=initialDate, end_dt=finalDate, agl_charge=AGLCharge, gas_usage=gasUsage, acct_id=account, bill_dt= date.today(), rs_cd=rateSchedule, calc_amt=totalCost)
    
    billOutput(bill, path=billOutput_path)
    addtoBillTable(bill)
    #billOutput(account, initialDate, finalDate, gasUsage, AGLCharge, usageCharge, path=billOutput_path)
    # Note: billOutput methods aren't logged yet in the case that they get changed in the future
