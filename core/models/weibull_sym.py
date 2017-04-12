from sympy import *
from sympy.tensor.array import Array
#from sympy import Sum, factorial
from sympy.utilities.lambdify import lambdastr

class Weibull():
    def __init__(self, kVec, tVec):
        self.kVec = kVec              #Failure Counts (FC)
        self.tVec = tVec              #Time interval vector
        self.kVec_len = len(self.kVec)      #Length of FC
        self.total_failures = sum(self.kVec)   #Sum of all recorded failures
        self.total_time = sum(self.tVec)       #Sum of all time intervals
        self.tn = self.tVec[-1]                 #Last time interval
        self.n = len(self.tVec)             #Length of time interval vector
        self.a, self.b, self.c = symbols('a b c')
        self.gen_logL_eqn()

    def gen_logL_eqn(self):
        self.k = IndexedBase('k')
        self.t = IndexedBase('t')
        self.i = symbols('i', cls=Idx)
        term1 = Sum(self.k[self.i], (self.i, 0, self.n-1))* ln(self.a)
        term2 = self.k[0] * ln(1 - exp(-self.b * self.t[0]**self.c))
        t3_num = exp(-self.b * self.t[self.i-1]**self.c) - exp(-self.b * self.t[self.i]**self.c)
        term3 = Sum((self.k[self.i] * ln(t3_num)), (self.i, 1, self.n-1))
        term4 = self.a*(1 - exp(-self.b * self.tn**self.c))
        term5 = Sum(ln(factorial(self.k[self.i])), (self.i, 0, self.n-1))

        self.logL_eqn = term1 + term2 + term3 - term4 - term5

    def gen_Da(self):
        return diff(self.logL_eqn, self.a)


    def logL(self, a, b, c):
        subst = [(self.a, a), (self.b, b), (self.c, c)]
        for x, kv in enumerate(self.kVec):
            subst.append((self.k[x], kv))
            subst.append((self.t[x], self.tVec[x]))
        #result = self.logL_eqn.doit().subs(subst).evalf()
        result = self.logL_eqn.doit()
        return result
    
    def logL_alt(self, a, b, c):
        subst = [(self.a, a), (self.b, b), (self.c, c)]
        for x, kv in enumerate(self.kVec):
            subst.append((self.k[x], kv))
            subst.append((self.t[x], self.tVec[x]))
        ll = lambdastr((self.a, self.b, self.c, self.k, self.t), self.logL_eqn.doit())
        print(ll(a, b, c))