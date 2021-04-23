from functions import *
from queryTest import *

cycCode = getCycCode()
print(cycCode)

accountsToProcess = getAccountsToProcess(cycCode)
print(accountsToProcess)

for account in accountsToProcess:
    billEndDates = retrieveBillHistory(account)
    mostRecentDate = findMostRecentBill(billEndDates)
    startDate = createStartDate(mostRecentDate, account)
    serviceAgreement = getSA(account)
    servicePoint = getSP(serviceAgreement)
    meter = getMeter(servicePoint)
    gasUsage = getGasUsage(meter, startDate)


print(startDate)
