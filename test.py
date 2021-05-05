from functions import *

SA = getSA('act940trc1')
print(SA)
SP = getSP(SA)
print(SP)
meter = getMeter(SP)
print(meter)

print(getTotalCost('act940trc1', 50))