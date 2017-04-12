import sys
import os
sys.path.append(os.path.abspath("../"))
#from weibull_mpm import Weibull
from models import Weibull
import math


class TestWeibull:
    kVec = [1, 0, 1, 15, 15, 32, 29, 45, 34, 67, 41, 71, 77, 80, 80, \
            42, 60, 92, 31, 68, 51, 51, 30, 29, 31, 20, 31, 30, 7, 15, 3, 4, 15]
    tVec = [i+1 for i in range(len(kVec))]
    w = Weibull(kVec, tVec)
    a = 33.0
    b = 0.0001
    c = 0.9
    #a = 1198.0 
    #b = 2.1354
    #c = 1.0
    
    def test_tf(self):
        assert self.w.total_failures == 1198

    def test_aMLE(self):
        aMLE = self.w.aMLE(self.w.total_failures, self.w.tn, self.b, self.c)
        assert abs(aMLE) ==  36.3007
            
    def test_bMLE(self):
        bMLE = self.w.bMLE(self.b, self.a, self.c, self.tVec)
        assert abs(bMLE) == 1.19649 * 10**7

    def test_cMLE(self):
        cMLE = self.w.cMLE(self.c, self.a, self.b, self.tVec)
        assert abs(cMLE) ==  4526.97

    def test_logL(self):
        logL = self.w.logL(self.a, self.b, self.c)
        assert abs(logL-(-10820.5)) < 0.1 


kVec = [1, 0, 1, 15, 15, 32, 29, 45, 34, 67, 41, 71, 77, 80, 80, \
           42, 60, 92, 31, 68, 51, 51, 30, 29, 31, 20, 31, 30, 7, 15, 3, 4, 15]
tVec = [i+1 for i in range(len(kVec))]
for i,k in enumerate(kVec):
    print("{},{}".format(tVec[i],k))
#w = Weibull(kVec, tVec)
#w.ECM()
#print(w.logL(1198.0, 2.1354, 1.0))
#print(w.logL(33, 0.0001, 0.9))
#print(w.gen_Da())
#w.logL_alt(33, 0.0001, 0.9)

