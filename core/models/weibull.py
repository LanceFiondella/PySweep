import math
import numpy as np
from scipy.optimize import fsolve

class Weibull():
    def __init__(self, kVec, tVec):
        self.kVec = np.array(kVec)     #Failure Counts (FC)
        self.tVec = np.array(tVec) #Time interval vector
        self.kVec_len = np.size(self.kVec) #Length of FC
        self.total_failures = self.kVec.sum() #Sum of all recorded failures
        self.total_time = self.tVec.sum() #Sum of all time intervals
        self.tn = self.tVec[-1] #Last time interval
        self.n = np.size(self.tVec) #Length of time interval vector

        self.estimate_parameters()

    def estimate_parameters(self):
        self.kVecCumul = np.cumsum(self.kVec)
        #Initial estimates
        self.a0 = 1.0*self.total_failures
        self.b0 = 1.0*self.total_failures/self.total_time
        self.c0 = 1.0
        #self.result = fsolve(self.MLE, [self.a0, self.b0, self.c0], (self.kVec, self.tVec), xtol=1e-24, maxfev=100000)
        self.result = fsolve(self.MLE, [self.a0, self.b0, self.c0], (self.kVec, self.tVec), maxfev=100000)
        (self.a, self.b, self.c) = self.result
        print(self.mvf())

    def aMLE(self, ip, *args):
        a = ip
        b = args[0]
        c = args[1]
        kVec = args[2]
        tVec = args[3]

    def MLE(self, ip, *args):
        print(ip)
        a = ip[0]
        b = ip[1]
        c = ip[2]
        kVec = args[0]
        tVec = args[1]
        n = np.size(kVec)


        sumi = [0,0,0]
        for i in range(n):
            sumi[0] += kVec[i]/a

        for i in range(1,n):
            powi = math.pow(tVec[i],c)
            expi = math.exp(-b * powi)

            powi1 = math.pow(tVec[i-1],c)
            expi1 = math.exp(-b * math.pow(tVec[i-1],c))

            sumi[1] += ((expi * powi - expi1 * powi1) * kVec[i]) / (expi1 - expi)
            sumi[2] += (b * (expi * powi * math.log(tVec[i]) - expi1 * powi1 * math.log(tVec[i])) * kVec[i]) / (expi1 - expi)

        #print(-b * math.pow(tVec[-1], c))
        exptn = math.exp(-b * math.pow(tVec[-1], c))
        expt1 = math.exp(b * math.pow(tVec[1], c))
        
        F1 = (-1 + exptn) + sumi[0]
        F2 = (-a + exptn) + ((kVec[1] * math.pow(tVec[1], c)) / (expt1 - 1)) + sumi[1]
        F3 = (-a * b * exptn * math.pow(tVec[-1], c) * math.log(tVec[-1])) + ((b * math.log(tVec[1]) * kVec[1] * math.pow(tVec[1], c)) / (expt1 - 1)) + sumi[2]
        return [F1, F2, F3]





    
    def exp(self,t):
        """Returns exponenial part of Weibull for use in other functions"""
        self.ex = math.exp(-1 * self.b * math.pow(t,self.c))
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


