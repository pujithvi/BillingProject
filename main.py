from functions import *
from queryTest import *

cycCode = getCycCode()
print(cycCode)

accountsToProcess = getAccountsToProcess(cycCode)
print(accountsToProcess)

# for account in accountsToProcess:
    #billEndDates = retrieveBillHistory(account)
    #mostRecentDate = findMostRecentBill(billEndDates)
    #startDate = createStartDate(mostRecentDate, account)

#print(startDate)
