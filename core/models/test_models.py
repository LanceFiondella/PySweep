from weibull import Weibull
import math

kVec = [1, 0, 1, 15, 15, 32, 29, 45, 34, 67, 41, 71, 77, 80, 80,\
        42, 60, 92, 31, 68, 51, 51, 30, 29, 31, 20, 31, 30, 7, 15, 3, 4, 15]

tVec = [i+1 for i in range(len(kVec))]

w = Weibull(kVec, tVec)
a = 33.0
b = 0.0001
c = 0.9

print(w.total_failures)
print(w.total_failures/(1 - math.exp(-0.0001 * 33**0.9)))
print(w.bMLE([0.0001],33.0, 0.9, tVec))
print(w.cMLE([0.9], 33.0, 0.0001, tVec))
#print(w.logL(a, b, c))
#print(w.a, w.b, w.c)