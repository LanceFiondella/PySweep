from mpmath import mp, nsum, log, factorial, exp, findroot, mpmathify, power
import numpy as np

mp.dps = 15 #Set the precision of calculations 
mp.pretty =  True #Set pretty print to True

class Weibull():
    def __init__(self, kVec, tVec):
        self.kVec = kVec              #Failure Counts (FC)
        self.tVec = tVec              #Time interval vector
        self.kVec_len = len(self.kVec)      #Length of FC
        self.total_failures = sum(self.kVec)   #Sum of all recorded failures
        self.total_time = sum(self.tVec)       #Sum of all time intervals
        self.tn = self.tVec[-1]                 #Last time interval
        self.n = len(self.tVec)             #Length of time interval vector

        self.ECM()

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
        
        limits_b = []
        limits_c = []
        
        while(self.ll_error > pow(10,-6)):
            print("Iteration number : {}".format(self.j))
            self.a_est = self.aMLE(self.total_failures, self.tn, self.brule[self.j], self.crule[self.j])
            self.arule.append(self.a_est)
            print("Estimated a: {}".format(self.a_est))
            
            limits_b = self.MLElim(self.bMLE, self.brule[self.j],  c=self.crule[self.j], a=self.arule[self.j+1])    
            self.b_est = findroot(self.bMLE, limits_b, tol=1e-15, solver = 'illinois')
            #self.b_est = findroot(self.bMLE, self.brule[self.j], tol=1e-24, solver = 'halley')
            print("Estimated b : {}".format(self.b_est))
            self.brule.append(self.b_est)
            

            #if len(limits_c) == 0:
            limits_c = self.MLElim(self.cMLE, self.crule[self.j], a=self.arule[self.j+1], b=self.brule[self.j+1])    
            self.c_est = findroot(self.cMLE, limits_c, tol=1e-15, solver = 'illinois')
            #self.c_est = findroot(self.cMLE, self.crule[self.j], tol=1e-24, solver = 'halley')
            print("Estimated c : {}".format(self.c_est))
            self.crule.append(self.c_est)
            

            self.ll_list.append(self.logL(self.a_est, self.b_est, self.c_est))
            self.j += 1
            self.ll_error = self.ll_list[self.j] - self.ll_list[self.j-1]
            print("Log Likelihood error = {}".format(self.ll_error))
            self.ll_error_list.append(self.ll_error)
            
            print("------------------------------------------------------------------------")
        print(self.ll_list[-1], self.arule[-1], self.brule[-1], self.crule[-1])
        
    def logL(self, a, b, c):
        """
        Loglikelihood function
        """
        sum_kveci_loga = 0
        sum_kveci_logexp = 0
        sum_log_kveci_fac = 0
        
        for i in range(self.kVec_len):
            sum_kveci_loga += self.kVec[i] * log(a)
            #num = mp.mpf(str())
            #fact = factorial(num)
            sum_log_kveci_fac += log(factorial(self.kVec[i]))
            if i > 0:
                #print(self.expo(i-1, b, c) - self.expo(i, b, c))
                sum_kveci_logexp += self.kVec[i] * log(self.expo(i-1, b, c) - self.expo(i, b, c))
        
        print(sum_kveci_logexp - sum_log_kveci_fac + self.kVec[0] * log(1 - self.expo(0, b, c)))
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
        return total_failures/(1 - exp(-b *  pow(tn,c)))
        

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
