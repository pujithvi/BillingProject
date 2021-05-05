from functions import *
from queryTest import *
import datetime
import os

directory = os.getcwd()
for file in os.scandir(directory):
    if (file.path.endswith('Log.txt') and file.is_file()):
        os.remove(file.path)
        # logFile = open(file.path, 'r+')
        # logFile.truncate(0)
        # logFile.close()

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
    except Exception as e:
        print('No service agreement for account ' + account)
        logger(account, str(e), 'getSA')
        billOutput(account = account, fail=True, text = "No service agreement for this account." )
        continue

    # print(serviceAgreement)
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
    billOutput(account, initialDate, finalDate, gasUsage, AGLCharge, usageCharge)


