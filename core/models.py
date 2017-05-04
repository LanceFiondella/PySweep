from mpmath import mp, fsum, log, factorial, exp, findroot, mpmathify, power
import numpy as np
import scipy.misc
from scipy.optimize import fsolve, root, ridder
import itertools
import math

mp.dps = 30 #Set the precision of calculations 
mp.pretty =  True #Set pretty print to True

class WeibullNumpy():
    def __init__(self, kVec, tVec):
        self.kVec = np.array(kVec, dtype=np.longdouble)              #Failure Counts (FC)
        self.tVec = np.array(tVec, dtype=np.longdouble)              #Time interval vector
        self.kVec_cumu_sum = np.cumsum(self.kVec)
        self.kVec_len = np.size(self.kVec)      #Length of FC
        self.total_failures = self.kVec.sum()   #Sum of all recorded failures
        self.total_time = self.tVec.sum()       #Sum of all time intervals
        self.tn = self.tVec[-1]                 #Last time interval
        self.n = np.size(self.tVec)             #Length of time interval vector

        self.results = self.ECM()
        self.complete_MVF()
        self.complete_FI()


    def ECM(self):
        """
        ECM Algorithm implementation
        """
        self.kVecCumul = np.cumsum(self.kVec)
        #Initial estimates
        self.arule = [1.0*self.total_failures]
        self.brule = [1.0*self.total_failures/self.total_time]
        self.crule = [1.0]

        self.ll_list = [self.logL(self.arule[0], self.brule[0], self.crule[0])]
        self.ll_error_list = []
        self.ll_error = 1
        self.j = 0
        while(self.ll_error > np.power(10.0,-10)):
            self.a_est = self.aMLE(self.total_failures, self.tn, self.brule[self.j], self.crule[self.j])
            self.arule.append(self.a_est)
            #print("Estimated a: {}".format(self.a_est))

            
            if self.j == 0:
                limits_b = self.MLElim(self.bMLE, self.brule[self.j], self.arule[self.j+1], self.crule[self.j], self.tVec)
            else:
                limits_b = [self.brule[self.j]/2, self.brule[self.j]*2]
            b_args = (self.arule[self.j+1], self.crule[self.j], self.tVec)
            self.b_est = float(findroot(self.bMLE, limits_b, tol=1e-10, solver = 'anderson', verify=False))
            #self.b_est = ridder(self.bMLE, limits_b[0], limits_b[1], b_args)
            #print("Estimated b : {}".format(self.b_est))
            self.brule.append(self.b_est)
            
            
            c_args = (self.arule[self.j+1], self.brule[self.j+1], self.tVec)
            #self.c_est = fsolve(self.cMLE, self.crule[j], c_args)
            if self.j == 0:
                #print("j is 0 <-------------------------------------------------------------")
                limits_c = self.MLElim(self.cMLE, self.crule[self.j], self.arule[self.j+1], self.brule[self.j+1], self.tVec)
            else:
                #limits = self.MLElim(self.cMLE, self.crule[j], self.arule[j+1], self.brule[j+1], self.tVec)
                limits_c = [self.crule[self.j]/2, self.crule[self.j]*2]
            


            #print("c limits:")
            #print(limits)
            #self.c_est = ridder(self.cMLE, limits_c[0], limits_c[1], c_args)
            self.c_est = float(findroot(self.cMLE, limits_c, tol=1e-9, solver = 'anderson', verify=False))
            #print("Estimated c : {}".format(self.c_est))
            self.crule.append(self.c_est)

            self.ll_list.append(self.logL(self.a_est, self.b_est, self.c_est))
            self.j += 1
            self.ll_error = self.ll_list[self.j] - self.ll_list[self.j-1]
            self.ll_error_list.append(self.ll_error)
        #print('Total iterations : {} '.format(j))    
        #print(self.ll_list[-1], self.arule[-1], self.brule[-1], self.crule[-1])
        return {'ll':self.ll_list[-1], 'a':self.arule[-1], 'b':self.brule[-1], 'c':self.crule[-1]}
        
    def logL(self, a, b, c):
        """
        Loglikelihood function
        """
        sum_kveci_loga = 0
        sum_kveci_logexp = 0
        sum_log_kveci_fac = 0
        
        for i in range(self.kVec_len):
            sum_kveci_loga += self.kVec[i] * np.log(a)
            sum_log_kveci_fac += np.log(scipy.misc.factorial(int(self.kVec[i])))
            if i > 0:
                sum_kveci_logexp += self.kVec[i] * self.log_diff(i, b, c)
                
        
        #print(sum_kveci_logexp - sum_log_kveci_fac + self.kVec[0] * np.log(1 - self.expo(0, b, c)))
        logL = sum_kveci_loga + (self.kVec[0] * np.log(1 - self.expo(0, b, c))) + sum_kveci_logexp - a * (1 - self.expo(-1, b, c)) - sum_log_kveci_fac
        return logL

    def log_diff(self, i , b, c):
        if self.expo(i-1, b, c) - self.expo(i, b, c) != 0:
            return np.log(self.expo(i-1, b, c) - self.expo(i, b, c))
        else:
            return float(log(expo_mp(i-1) - expo_mp(i)))


    def expo(self, x, b, c):
        """
        Exponential part = -b * tx^c  
        """
        b = float(b)
        c = float(c)
        result = np.exp(-b * np.power(self.tVec[x],c))
        return result
        
    def expo_mp(self, x, b, c):
        return exp(-b * power(float(self.tVec[x]),c))

    def aMLE(self, total_failures, tn, b, c):
        """
        Estimation of a
        """
        b = float(b)
        c = float(c)
        return float(total_failures/(1 - np.exp(-b *  np.power(tn,c))))
        

    def bMLE(self, ip, *args):
        """
        Estimation of b
        """
        #print(args)
        b = float(ip)
        
        a = self.arule[self.j+1]
        c = self.crule[self.j]
        
        tVec = self.tVec
        tn = tVec[-1]
        sum_k = 0
        n = np.size(tVec)
        
        for i in range(n):
            if i >0:
                numer = (np.power(self.tVec[i],c) * self.expo(i, b, c) - np.power(self.tVec[i-1],c) * self.expo(i-1, b, c))
                denom = (self.expo(i-1, b, c) - self.expo(i, b, c))
            else:
                numer = (np.power(self.tVec[i],c) * self.expo(i, b, c))
                denom = ( 1 - self.expo(i, b, c))
            if (denom == 0 or numer == 0) and i >0:
                denom = exp(-mp.mpf(str(b)) * power(str(self.tVec[i-1]),mp.mpf(str(c)))) - exp(-mp.mpf(str(b)) * power(str(self.tVec[i]),mp.mpf(str(c))))
                numer = (power(float(self.tVec[i]),c) * self.expo_mp(i, b, c) - power(float(self.tVec[i-1]),c) * self.expo_mp(i-1, b, c))
                
            
            
            sum_k += self.kVec[i] * float(numer / denom) 
            #print("sumk : {} * {} / {}  ::  b = {}, c = {}".format(self.kVec[i], numer, denom, b, c) )

        bprime =  sum_k - a * np.power(self.tVec[-1],c) * self.expo(-1, b, c)
        #bprime =  b - sum_k
        
        #print("Bprime : {} - ({} - {}) ".format(b, sum_k, a * np.power(self.tVec[-1],c) * self.expo(-1, b, c)))
        return float(bprime)

    def MLElim(self, func, val, *args):
        maxIterations = 100
        leftEndPoint = val / 2
        #print(args)
        leftEndPointMLE = func(leftEndPoint, args[0], args[1], args[2])
        rightEndPoint = 2 * val
        rightEndPointMLE = func(rightEndPoint, args[0], args[1], args[2])
        i = 0
        while(leftEndPointMLE * rightEndPointMLE > 0 & i <= maxIterations):
            #print(leftEndPoint, rightEndPoint)
            leftEndPoint = leftEndPoint / 2
            leftEndPointMLE = func(leftEndPoint, args[0], args[1], args[2])
            rightEndPoint = 2 * rightEndPoint
            rightEndPointMLE = func(rightEndPoint, args[0], args[1], args[2])
            i = i + 1
        #print(leftEndPointMLE, rightEndPointMLE)
        return (float(leftEndPoint), float(rightEndPoint))

    def cMLE(self, ip, *args):
        """
        Estimation of c
        """
        c = float(ip)
        a = float(self.arule[self.j+1])
        b = float(self.brule[self.j+1])
        #print("a = {}, b = {}, c = {}".format(a, b, c))
        tVec = self.tVec
        tn = tVec[-1]
        exp_tn = np.exp(-b * np.power(tn,c))
        n = np.size(tVec)
        sum_k = 0
        for i in range(n):
            if i > 0:
                numer = (np.power(self.tVec[i],c) * self.expo(i, b, c) * np.log(tVec[i]) - np.power(self.tVec[i-1],c) * self.expo(i-1, b, c) * np.log(tVec[i-1]))
                denom = (self.expo(i-1, b, c) - self.expo(i, b, c))
                
            else:
                numer = (np.power(self.tVec[i],c) * self.expo(i, b, c) * np.log(tVec[i]))
                denom = (1 - self.expo(i, b, c))
            if (denom == 0 or numer==0) and i >0:
                denom = exp(-mp.mpf(str(b)) * power(str(self.tVec[i-1]),mp.mpf(str(c)))) - exp(-mp.mpf(str(b)) * power(str(self.tVec[i]),mp.mpf(str(c))))
                numer = (power(float(self.tVec[i]),c) * self.expo_mp(i, b, c) * log(float(self.tVec[i])) - power(float(self.tVec[i-1]),c) * self.expo_mp(i-1, b, c) * log(float(self.tVec[i-1])))
            
            
            #print ("{} / {}".format(type(numer),type(denom)))
            ratio = numer / denom
            #print(ratio) 
            sum_k += self.kVec[i] * b * float(ratio)
            
        
        

        cprime = sum_k - a * b * np.power(self.tVec[-1],c) * self.expo(-1, b, c) * np.log(tVec[-1])
        return float(cprime)

    def get_peak_loc(self):
        max_intensity = float('-inf')
        max_intensity_index = 0
        for i in range(len(self.tVec)):
            fi = self.failure_intensity(self.a_est, self.b_est, self.c_est, i)
            if fi > max_intensity:
                max_intensity = fi
                max_intensity_index = i
        return max_intensity_index 

    def failure_intensity(self, a, b, c, i):
        a = float(a)
        b = float(b)
        c = float(c)
        return a * b * c * self.expo(i, b, c) * np.power(self.tVec[i], c-1)

    def fi_t(self, a, b, c, t):
        return a * b * c * np.exp(-b * np.power(t,c)) * np.power(t, c-1)

    def MVF(self, t, a, b, c):
        """
        MVF value at a single point in time
        Use completeMVF to get all MVF values
        """
        a = float(a)
        b = float(b)
        c = float(c)
        t = float(t)
        return a * (1 - np.exp(-b * np.power(t, c)))

    def complete_MVF(self):
        """
        Calculates MVF values for all tVec. It is assumed that MLEs are calculated.
        """
        self.MVF_vals = []
        for t in self.tVec:
            self.MVF_vals.append(self.MVF(t, self.a_est, self.b_est, self.c_est))
        return self.MVF_vals

    def complete_FI(self):
        """
        Calculates Failure Intensity values for all tVec. It is assumed that MLEs are calculated.
        """
        self.FI_vals = []
        for i in range(len(self.tVec)):
            self.FI_vals.append(self.failure_intensity(self.a_est, self.b_est, self.c_est, i))

    @property
    def error_delta(self):
        """
        Calculates the differene between the actual error and estimated error for each t in tVec
        """
        return self.kVec - self.MVF_vals

    @property
    def rel_delta(self):
        return (self.kVec - self.MVF_vals) * 100 / self.kVec

    @property
    def MVF_cumu_sum(self):
        return np.cumsum(self.MVF_vals)

    @property
    def cumu_delta(self):
        return self.kVec_cumu_sum - self.MVF_cumu_sum

    @property
    def cumu_rel_delta(self):
        return self.cumu_delta * 100 / self.kVec_cumu_sum

class WeibullMP():
    def __init__(self, kVec, tVec):
        #self.kVec = [mp.mpf(k) for k in kVec]              #Failure Counts (FC)
        self.kVec = [float(k) for k in kVec]
        #self.tVec = [mp.mpf(t) for t in tVec]              #Time interval vector
        self.tVec = [float(t) for t in tVec]
        self.kVec_len = len(self.kVec)      #Length of FC
        self.total_failures = np.sum(self.kVec)   #Sum of all recorded failures
        self.total_time = np.sum(self.tVec)       #Sum of all time intervals
        self.tn = self.tVec[-1]                 #Last time interval
        self.n = len(self.tVec)             #Length of time interval vector
        self.kVec_cumu_sum = [i for i in itertools.accumulate(self.kVec)]
        self.ECM()
        self.complete_MVF()
        self.complete_FI()

    def ECM(self):
        """
        ECM Algorithm implementation
        """
        #self.kVecCumul = np.cumsum(self.kVec)
        #Initial estimates
        self.arule = [1.0*self.total_failures]
        self.brule = [1.0*self.total_failures/self.total_time]
        self.crule = [1.0]

        self.ll_list = [self.logL(self.arule[0], self.brule[0], self.crule[0])]
        self.ll_error_list = []
        self.ll_error = 1
        self.j = 0
        
        limits_b = []
        limits_c = []
        
        while(self.ll_error > pow(10,-6)):
            print("Iteration number : {}".format(self.j))
            self.a_est = self.aMLE(self.total_failures, self.tn, self.brule[self.j], self.crule[self.j])
            self.arule.append(self.a_est)
            #print("Estimated a: {}".format(self.a_est))
            
            if self.j == 0:
                limits_b = self.MLElim(self.bMLE, self.brule[self.j],  c=self.crule[self.j], a=self.arule[self.j+1])    
            else:
                limits_b = [self.brule[self.j]/2, self.brule[self.j]*2]
            
            self.b_est = findroot(self.bMLE, limits_b, tol=1e-10, solver = 'anderson')
            #self.b_est = ridder(self.bMLE, limits_b[0], limits_b[1])
            #self.b_est = findroot(self.bMLE, self.brule[self.j], tol=1e-24, solver = 'halley')
            #print("Estimated b : {}".format(self.b_est))
            self.brule.append(self.b_est)
            

            if self.j == 0:
                limits_c = self.MLElim(self.cMLE, self.crule[self.j], a=self.arule[self.j+1], b=self.brule[self.j+1])    
            else:
                limits_c = [self.crule[self.j]/2, self.crule[self.j]*2]
            
            self.c_est = findroot(self.cMLE, limits_c, tol=1e-10, solver = 'anderson')
            #self.c_est = ridder(self.cMLE, limits_c[0], limits_c[1])
            #self.c_est = findroot(self.cMLE, self.crule[self.j], tol=1e-24, solver = 'halley')
            #print("Estimated c : {}".format(self.c_est))
            self.crule.append(self.c_est)
            

            self.ll_list.append(self.logL(self.a_est, self.b_est, self.c_est))
            self.j += 1
            self.ll_error = self.ll_list[self.j] - self.ll_list[self.j-1]
            #print("Log Likelihood error = {}".format(self.ll_error))
            self.ll_error_list.append(self.ll_error)
            
            #print("------------------------------------------------------------------------")
            
        print(self.ll_list[-1], self.arule[-1], self.brule[-1], self.crule[-1])
        
    def logL(self, a, b, c):
        """
        Loglikelihood function
        """
        sum_kveci_loga = 0
        sum_kveci_logexp = 0
        sum_log_kveci_fac = 0
        
        for i in range(self.kVec_len):
            sum_kveci_loga += self.kVec[i] * np.log(a)
            #num = mp.mpf(str())
            #fact = factorial(num)
            sum_log_kveci_fac += log(factorial(self.kVec[i]))
            if i > 0:
                #print(self.expo(i-1, b, c) - self.expo(i, b, c))
                sum_kveci_logexp += self.kVec[i] * log(self.expo(i-1, b, c) - self.expo(i, b, c))
        
        #print(sum_kveci_logexp - sum_log_kveci_fac + self.kVec[0] * log(1 - self.expo(0, b, c)))
        logL = sum_kveci_loga + (self.kVec[0] * log(1 - self.expo(0, b, c))) + sum_kveci_logexp - a * (1 - self.expo(-1, b, c)) - sum_log_kveci_fac
        return logL



    def expo(self, x, b, c):
        """
        Exponential part = -b * tx^c  
        """
        #print(-b * self.tVec[x]**c)

        #return exp(-b * self.tVec[x]**c)
        return exp(-b * power(self.tVec[x],c))

    def aMLE(self, total_failures, tn, b, c):
        """
        Estimation of a
        """
        return total_failures/(1 - np.exp(-b *  np.power(tn,c)))
        

    def bMLE(self, ip, **kwargs):
        """
        Estimation of b
        """
        b = ip
        if len(kwargs.keys()) != 0:
            a = kwargs['a']
            c = kwargs['c']
        else: 
            a = self.arule[self.j+1]
            c = self.crule[self.j]
        
        tVec = self.tVec
        tn = tVec[-1]
        sum_k = 0
        n = np.size(tVec)
        
        for i in range(n):
            if i >0:
                numer = (pow(self.tVec[i],c) * self.expo(i, b, c) - pow(self.tVec[i-1],c) * self.expo(i-1, b, c))
                denom = (self.expo(i-1, b, c) - self.expo(i, b, c))
            else:
                numer = (pow(self.tVec[i],c) * self.expo(i, b, c))
                denom = ( 1 - self.expo(i, b, c))
            sum_k += self.kVec[i] * numer / denom 
            #print("sumk : {} * {} / {}  ::  b = {}, c = {}".format(self.kVec[i], numer, denom, b, c) )

        bprime = sum_k - a * pow(self.tVec[-1],c) * self.expo(-1, b, c)
        bprime = b - bprime
        
        #print("Bprime : {} - ({} - {}) ".format(b, sum_k, a * self.tVec[-1]**c * self.expo(-1, b, c)))
        return bprime

    def MLElim(self, func, val, **kwargs):
        maxIterations = 100
        leftEndPoint = val / 2
        #print(args)
        leftEndPointMLE = func(leftEndPoint, **kwargs)
        rightEndPoint = 2 * val
        rightEndPointMLE = func(rightEndPoint, **kwargs)
        i = 0
        while(leftEndPointMLE * rightEndPointMLE > 0 & i <= maxIterations):
            #print(leftEndPoint, rightEndPoint)
            leftEndPoint = leftEndPoint / 2
            leftEndPointMLE = func(leftEndPoint, **kwargs)
            rightEndPoint = 2 * rightEndPoint
            rightEndPointMLE = func(rightEndPoint, **kwargs)
            i = i + 1
        print("Max iterations : " + str(i))
        return [leftEndPoint, rightEndPoint]

    def cMLE(self, ip, **kwargs):
        """
        Estimation of c
        """
        c = ip
        if len(kwargs.keys()) != 0:
            a = kwargs['a']
            b = kwargs['b']
        else:
            a = self.arule[self.j+1]
            b = self.brule[self.j+1]
        tVec = self.tVec
        tn = tVec[-1]
        exp_tn = exp(-b * pow(tn,c))
        n = np.size(tVec)
        sum_k = 0
        for i in range(n):
            tVeci = tVec[i]
            tVeci1 = tVec[i-1]
            if i > 0:
                numer = (pow(tVeci,c) * self.expo(i, b, c) * log(tVeci) - pow(tVeci1,c) * self.expo(i-1, b, c) * log(tVeci1))
                denom = (self.expo(i-1, b, c) - self.expo(i, b, c))
            else:
                numer = (pow(tVeci,c) * self.expo(i, b, c) * log(tVeci))
                denom = (1 - self.expo(i, b, c))
            sum_k += self.kVec[i] * b * (numer / denom)

        
        cprime = sum_k - a * b * pow(self.tn,c) * self.expo(-1, b, c) * log(self.tn)
        return cprime

    def get_peak_loc(self):
        max_intensity = float('-inf')
        max_intensity_index = 0
        for i in range(len(self.tVec)):
            fi = self.failure_intensity(self.a_est, self.b_est, self.c_est, i)
            if fi > max_intensity:
                max_intensity = fi
                max_intensity_index = i
        return max_intensity_index 

    def failure_intensity(self, a, b, c, i):
        return a * b * c * self.expo(i, b, c) * power(self.tVec[i], c-1)

    def fi_t(self, a, b, c, t):
        return a * b * c * exp(-b * power(t,c)) * power(t, c-1)

    def MVF(self, t, a, b, c):
        """
        MVF value at a single point in time
        Use completeMVF to get all MVF values
        """
        return a * (1 - exp(-b * power(t, c)))

    def complete_MVF(self):
        """
        Calculates MVF values for all tVec. It is assumed that MLEs are calculated.
        """
        self.MVF_vals = []
        for t in self.tVec:
            self.MVF_vals.append(self.MVF(t, self.a_est, self.b_est, self.c_est))
        return self.MVF_vals

    def complete_FI(self):
        """
        Calculates Failure Intensity values for all tVec. It is assumed that MLEs are calculated.
        """
        self.FI_vals = []
        for i in range(len(self.tVec)):
            self.FI_vals.append(self.failure_intensity(self.a_est, self.b_est, self.c_est, i))

    @property
    def error_delta(self):
        """
        Calculates the differene between the actual error and estimated error for each t in tVec
        """
        return [self.kVec[i] - self.MVF_vals[i] for i in range(len(self.kVec))]

    @property
    def rel_delta(self):
        return [mp.mpf("inf") if self.kVec[i] == 0 else (self.kVec[i] - self.MVF_vals[i]) * 100 / self.kVec[i] for i in range(len(self.kVec))]
        
        #((self.kVec - self.MVF_vals) * 100 / self.kVec)

    @property
    def MVF_cumu_sum(self):
        return [i for i in itertools.accumulate(self.MVF_vals)]

    @property
    def cumu_delta(self):
        return [self.kVec_cumu_sum[i] - self.MVF_cumu_sum[i] for i in range(len(self.kVec_cumu_sum))]

    @property
    def cumu_rel_delta(self):
        return [self.cumu_delta[i] * 100 / self.kVec_cumu_sum[i] for i in range(len(self.kVec_cumu_sum))]
 
if __name__=="__main__":
    kVec = [1, 0, 1, 15, 15, 32, 29, 45, 34, 67, 41, 71, 77, 80, 80, \
            42, 60, 92, 31, 68, 51, 51, 30, 29, 31, 20, 31, 30, 7, 15, 3, 4, 15]
    tVec = [i+1 for i in range(len(kVec))]
    w = WeibullNumpy(kVec[:27], tVec[:27])
    print(w.results)
