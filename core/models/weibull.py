import math
import numpy as np
from scipy.optimize import fsolve, root

class Weibull():
    def __init__(self, kVec, tVec):
        self.kVec = np.array(kVec)     #Failure Counts (FC)
        self.tVec = np.array(tVec) #Time interval vector
        self.kVec_len = np.size(self.kVec) #Length of FC
        self.total_failures = self.kVec.sum() #Sum of all recorded failures
        self.total_time = self.tVec.sum() #Sum of all time intervals
        self.tn = self.tVec[-1] #Last time interval
        self.n = np.size(self.tVec) #Length of time interval vector

        #self.ECM()

    def ECM(self):
        self.kVecCumul = np.cumsum(self.kVec)
        #Initial estimates
        self.arule = [1.0*self.total_failures]
        self.brule = [1.0*self.total_failures/self.total_time]
        self.crule = [1.0]

        self.ll_list = [self.logL(self.arule[0], self.brule[0], self.crule[0])]
        self.ll_error_list = []
        self.ll_error = 1
        j = 0
        while(self.ll_error > 10**-15):
            
            self.a_est = self.total_failures/(1 - math.exp(-self.brule[j] *  self.tn**self.crule[j]))
            #print(a_est)
            self.arule.append(self.a_est)
            print("Estimated a: {}".format(self.a_est))

            b_args = (self.arule[j+1], self.crule[j], self.tVec)
            self.b_est = fsolve(self.bMLE, self.brule[j], b_args)
            print("Estimated b : {}".format(self.b_est))
            self.brule.append(self.b_est[0])

            c_args = (self.arule[j+1], self.brule[j+1], self.tVec)
            self.c_est = fsolve(self.cMLE, self.crule[j], c_args)
            print("Estimated c : {}".format(self.c_est))
            self.crule.append(self.c_est[0])

            self.ll_list.append(self.logL(self.a_est, self.b_est, self.c_est))
            self.ll_error = self.ll_list[j] - self.ll_list[j-1]
            self.ll_error_list.append(self.ll_error)
            j += 1
        print(self.ll_list[-1], self.arule[-1], self.brule[-1], self.crule[-1])
        
    def logL(self, a, b, c):
        sum_kveci_loga = 0
        sum_kveci_logexp = 0
        sum_log_kveci_fac = 0
        
        for i in range(self.kVec_len):
            sum_kveci_loga += self.kVec[i] * math.log(a)
            sum_log_kveci_fac += math.log(math.factorial(self.kVec[i]))
            if i > 0:
                #print(self.expo(i-1, b, c) - self.expo(i, b, c))
                sum_kveci_logexp += self.kVec[i] * math.log(self.expo(i-1, b, c) - self.expo(i, b, c))
        
        logL = sum_kveci_loga + (self.kVec[0] * math.log(1 - self.expo(0, b, c))) + sum_kveci_logexp - a * (1 - self.expo(-1, b, c)) - sum_log_kveci_fac
        return logL

    def expo(self, x, b, c):
        #print(b, c)
        return math.exp(-b * self.tVec[x]**c)

    def bMLE(self, ip, *args):
        print(args)
        b = ip[0]
        a = args[0]
        c = args[1]
        tVec = args[2]
        tn = tVec[-1]
        #print("In bMLE: {} {} {} ".format(a,b,c))
        exp_tn = math.exp(-b * tn**c)
        sum_k = 0
        n = np.size(tVec)
        
        for i in range(1,n):
            numer = (self.tVec[i]**c * self.expo(i, b, c) - self.tVec[i-1]**c * self.expo(i-1, b, c))
            denom = (self.expo(i-1, b, c) - self.expo(i, b, c))
            sum_k += self.kVec[i] * numer / denom 

        bprime = b - (sum_k - a * self.tVec[-1]**c * self.expo(-1, b, c) )
        #print("Bprime : {} ".format(bprime))
        return bprime

    def cMLE(self, ip, *args):
        c = ip[0]
        a = args[0]
        b = args[1]
        tVec = args[2]
        tn = tVec[-1]
        exp_tn = math.exp(-b * tn**c)
        n = np.size(tVec)
        sum_k = 0
        for i in range(1,n):
            numer = (self.tVec[i]**c * self.expo(i, b, c) * math.log(tVec[i]) - self.tVec[i-1]**c * self.expo(i-1, b, c) * math.log(tVec[i-1]))
            denom = (self.expo(i-1, b, c) - self.expo(i, b, c))
            sum_k += self.kVec[i] * b * (numer / denom)

        cprime = c - (sum_k - a * b * self.tVec[-1]**c * self.expo(-1, b, c) * math.log(tVec[-1]))
        return cprime

    
    def exp(self,t):
        """Returns exponenial part of Weibull for use in other functions"""
        self.ex = math.exp(-1 * self.b * t**self.c)
        return self.ex

    
    def cdf(self,t):
        """Returns the Cumulative Distribution function (cdf) for Weibull"""
        return 1 - self.exp(t) 

    
    def pdf(self, t):
        """Returns Probability Density Function (pdf) for Weibull"""
        return self.b * self.c * self.exp(t) * math.pow(t, (self.c - 1))

    
    def mvf(self):
        """Returns Mean Value function (mvf) for Weibull"""
        result = []
        for t in self.tVec:
            result.append(self.a * self.cdf(t))
        return result

    
    def fi(self):
        """Returns Failure Intensity / Instantaneous Failure Rate for
        Weibull"""
        return self.a * self.pdf


