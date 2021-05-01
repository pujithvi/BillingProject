from functions import *
from queryTest import *
import datetime

cycCode = getCycCode()
print(cycCode)

accountsToProcess = getAccountsToProcess(cycCode)
print(accountsToProcess)

for account in accountsToProcess:
    billEndDates = retrieveBillEndDates(account)
    print(billEndDates)
    mostRecentDate = findMostRecentEndDate(billEndDates)
    print(mostRecentDate)
    startDate = createStartDate(mostRecentDate, account)
    print(startDate)
    serviceAgreement = getSA(account)
    print(serviceAgreement)
    servicePoint = getSP(serviceAgreement)
    print(servicePoint)
    meter = getMeter(servicePoint)
    print(meter)
    gasUsage = convertToTherms(getGasUsage(meter, startDate))
    print(gasUsage)
    totalCost = getTotalCost(account, gasUsage)


print(startDate)
