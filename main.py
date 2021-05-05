from functions import *
from billClass import *
from queryTest import *
import datetime
import os

directory = os.getcwd()
for file in os.scandir(directory):
    if (file.path.endswith('Log.txt') and file.is_file()):
        os.remove(file.path)

sql_selectMostRecentBill = '''
select bill_id from hs_ci_bill order by id desc
'''
cur.execute(sql_selectMostRecentBill)
mostRecentBill_id = cur.fetchone()[0]
bill_num = int(mostRecentBill_id.split('AS')[1].split('Y')[0]) + 1

AGLCharge_dictionary = {}
Rate_dictionary = {}

cycCode = getCycCode()
# print(cycCode)

accountsToProcess = getAccountsToProcess(cycCode)
print(accountsToProcess)

for account in accountsToProcess:

    print(account)

        # Need to do like this for every method
    try:
        billEndDates = retrieveBillEndDates(account)
        logger(account, method = 'retrieveBillEndDates', successful=True)
    except Exception as e:
        logger(account, str(e), 'retrieveBillEndDates')
        continue
   
    # print(billEndDates)
    mostRecentDate = findMostRecentEndDate(billEndDates)
    # print(mostRecentDate)
    startDate = createStartDate(mostRecentDate, account)
    #print('start date:', startDate)


    try:
        serviceAgreement = getSA(account)
        # print(serviceAgreement)
    except Exception as e:
        print('No service agreement for account ' + account)
        logger(account, str(e), 'getSA')
        billOutput(account = account, fail=True, text = "No service agreement for this account." )
        continue


    servicePoint = getSP(serviceAgreement)
    # print(servicePoint)
    meter = getMeter(servicePoint)
    #print('meter:', meter)
    initialDate, finalDate, gasUsage = getGasUsage(meter, startDate)
    gasUsage = convertToTherms(gasUsage)
    # print(gasUsage)

    rateSchedule = getRateSchedule(account)
    # print(rateSchedule)
    AGLCharge = getAGLFixedCharge(rateSchedule, AGLCharge_dictionary)
    # print(AGLCharge)
    usageCharge = calculateGasCharge(rateSchedule, gasUsage, Rate_dictionary)
    # print(usageCharge)

    totalCost = AGLCharge + usageCharge
 
    print(totalCost)
    #Could create a bill object and go from there
    # finish this: bill = Bill(bill_id='SFGAS' + str(bill_num) + 'Y21', )
    billOutput(account, initialDate, finalDate, gasUsage, AGLCharge, usageCharge)


