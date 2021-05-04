from functions import *
from queryTest import *
import datetime

AGLCharge_dictionary = {}
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
    try:
        serviceAgreement = getSA(account)
    except:
        print('No service agreement for account ' + account)
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
    usageCharge = calculateGasCharge(rateSchedule, gasUsage)
    # print(usageCharge)

    totalCost = AGLCharge + usageCharge
    #totalCost = getTotalCost(account, gasUsage)
    print(totalCost)


print(startDate)
