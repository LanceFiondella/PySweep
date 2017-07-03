import math
import numpy as np
from scipy.optimize import fsolve, root, ridder
from mpmath import mp, log, exp, power

mp.dps = 50 #Set the precision of calculations 
mp.pretty =  True #Set pretty print to True

class Weibull():
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
        j = 0
        while(self.ll_error > np.power(10.0,-5)):
            self.a_est = self.aMLE(self.total_failures, self.tn, self.brule[j], self.crule[j])
            self.arule.append(self.a_est)
            #print("Estimated a: {}".format(self.a_est))

            
            if j == 0:
                limits_b = self.MLElim(self.bMLE, self.brule[j], self.arule[j+1], self.crule[j], self.tVec)
            else:
                #limits_b = self.MLElim(self.bMLE, self.brule[j], self.arule[j+1], self.crule[j], self.tVec)
                limits_b = [self.brule[j]/2, self.brule[j]*2]
            b_args = (self.arule[j+1], self.crule[j], self.tVec)
            #self.b_est = root(self.bMLE, self.brule[j], b_args, method='krylov')
            self.b_est = ridder(self.bMLE, limits_b[0], limits_b[1], b_args)
            #print("Estimated b : {}".format(self.b_est))
            self.brule.append(self.b_est)
            
            
            c_args = (self.arule[j+1], self.brule[j+1], self.tVec)
            #self.c_est = fsolve(self.cMLE, self.crule[j], c_args)
            if j == 0:
                #print("j is 0 <-------------------------------------------------------------")
                limits = self.MLElim(self.cMLE, self.crule[j], self.arule[j+1], self.brule[j+1], self.tVec)
            else:
                #limits = self.MLElim(self.cMLE, self.crule[j], self.arule[j+1], self.brule[j+1], self.tVec)
                limits = [self.crule[j]/2, self.crule[j]*2]
            


            #print("c limits:")
            #print(limits)
            self.c_est = ridder(self.cMLE, limits[0], limits[1], c_args)
            #print("Estimated c : {}".format(self.c_est))
            self.crule.append(self.c_est)

            self.ll_list.append(self.logL(self.a_est, self.b_est, self.c_est))
            j += 1
            self.ll_error = self.ll_list[j] - self.ll_list[j-1]
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
            sum_log_kveci_fac += math.log(np.math.factorial(self.kVec[i]))
            if i > 0:
                sum_kveci_logexp += self.kVec[i] * np.log(self.expo(i-1, b, c) - self.expo(i, b, c))
        
        #print(sum_kveci_logexp - sum_log_kveci_fac + self.kVec[0] * np.log(1 - self.expo(0, b, c)))
        logL = sum_kveci_loga + (self.kVec[0] * np.log(1 - self.expo(0, b, c))) + sum_kveci_logexp - a * (1 - self.expo(-1, b, c)) - sum_log_kveci_fac
        return logL



    def expo(self, x, b, c):
        """
        Exponential part = -b * tx^c  
        """
        #print(-b * self.tVec[x]**c)
        return np.exp(-b * np.power(self.tVec[x],c))

    def aMLE(self, total_failures, tn, b, c):
        """
        Estimation of a
        """
        return total_failures/(1 - np.exp(-b *  np.power(tn,c)))
        

    def bMLE(self, ip, *args):
        """
        Estimation of b
        """
        #print(args)
        b = ip
        a = args[0]
        c = args[1]
        
        tVec = args[2]
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
            if denom == 0 and i >0:
                denom = exp(-mp.mpf(str(b)) * power(str(self.tVec[i-1]),c)) - exp(-mp.mpf(str(b)) * power(str(self.tVec[i]),c))
                numer = mp.mpf(float(numer))
            
            
            sum_k += self.kVec[i] * float(numer / denom) 
            #print("sumk : {} * {} / {}  ::  b = {}, c = {}".format(self.kVec[i], numer, denom, b, c) )

        bprime =  sum_k - a * np.power(self.tVec[-1],c) * self.expo(-1, b, c)
        #bprime =  b - sum_k
        
        #print("Bprime : {} - ({} - {}) ".format(b, sum_k, a * np.power(self.tVec[-1],c) * self.expo(-1, b, c)))
        return bprime

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
        return (leftEndPoint, rightEndPoint)

    def cMLE(self, ip, *args):
        """
        Estimation of c
        """
        c = ip
        a = args[0]
        b = args[1]
        #print("a = {}, b = {}, c = {}".format(a, b, c))
        tVec = args[2]
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
            if denom == 0 and i >0:
                denom = exp(-b * power(str(self.tVec[i-1]),c)) - exp(-b * power(str(self.tVec[i]),c))
                numer = mp.mpf(float(numer))
            
            
            #print ("{} / {}".format(type(numer),type(denom)))
            ratio = numer / denom
            #print(ratio) 
            sum_k += self.kVec[i] * b * float(ratio)
            
        
        

        cprime = sum_k - a * b * np.power(self.tVec[-1],c) * self.expo(-1, b, c) * np.log(tVec[-1])
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
        return a * b * c * self.expo(i, b, c) * np.power(self.tVec[i], c-1)

    def fi_t(self, a, b, c, t):
        return a * b * c * np.exp(-b * np.power(t,c)) * np.power(t, c-1)

    def MVF(self, t, a, b, c):
        """
        MVF value at a single point in time
        Use completeMVF to get all MVF values
        """
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
