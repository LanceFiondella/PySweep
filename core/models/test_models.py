from weibull import Weibull

kVec = [1, 0, 1, 15, 15, 32, 29, 45, 34, 67, 41, 71, 77, 80, 80,\
        42, 60, 92, 31, 68, 51, 51, 30, 29, 31, 20, 31, 30, 7, 15, 3, 4, 15]

tVec = [i+1 for i in range(len(kVec))]

w = Weibull(kVec, tVec)
#print(w.a, w.b, w.c)