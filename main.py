from functions import *
from queryTest import *
import datetime

logger.counter = 0
AGLCharge_dictionary = {}
Rate_dictionary = {}

cycCode = getCycCode()
# print(cycCode)

accountsToProcess = getAccountsToProcess(cycCode)
print(accountsToProcess)

for account in accountsToProcess:

    print(account)
    billEndDates = retrieveBillEndDates(account)
    # print(billEndDates)
    mostRecentDate = findMostRecentEndDate(billEndDates)
    # print(mostRecentDate)
    startDate = createStartDate(mostRecentDate, account)
    # print(startDate)

    # Need to do like this for every method
    try:
        serviceAgreement = getSA(account)
    except Exception as e:
        print('No service agreement for account ' + account)
        logger(account, str(e), 'getSA')
        continue

    # print(serviceAgreement)
    servicePoint = getSP(serviceAgreement)
    # print(servicePoint)
    meter = getMeter(servicePoint)
    # print(meter)
    gasUsage = convertToTherms(getGasUsage(meter, startDate))
    # print(gasUsage)

    rateSchedule = getRateSchedule(account)
    # print(rateSchedule)
    AGLCharge = getAGLFixedCharge(rateSchedule, AGLCharge_dictionary)
    # print(AGLCharge)
    usageCharge = calculateGasCharge(rateSchedule, gasUsage, Rate_dictionary)
    # print(usageCharge)

    totalCost = AGLCharge + usageCharge
    #totalCost = getTotalCost(account, gasUsage)
    print(totalCost)
    billOutput(account, gasUsage, AGLCharge, usageCharge)


print(startDate)
