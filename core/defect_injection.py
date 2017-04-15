import numpy as np

class DefectInjection():
    def __init__(self, data):
        self.detection_profile = np.array(data['dp']['data'])
        self.names = data['dp']['names']
        self.latent_defects = float(data['ld'])
        self.num_phases = np.size(self.detection_profile)
        self.total_defects = self.detection_profile.sum() + self.latent_defects
        self.profile_peak = 1 / np.sqrt(-2 * np.log(self.latent_defects/self.total_defects) / np.power(self.num_phases, 2))
        self.leakage_rate = self.detection_profile[-1]/self.detection_profile[-2]
        self.calc_dimat()

    def calc_dimat(self):
        self.di_matrix = np.zeros((self.num_phases, self.num_phases))
        for col in range(self.num_phases):
            for row in range(self.num_phases):
                if col == row:
                    self.di_matrix[row,col] = self.detection_profile[col] - self.di_matrix[:row,col].sum()
                elif col > row:
                    self.di_matrix[row,col] = self.di_matrix[row,col-1] * self.leakage_rate
        

    @property
    def D2(self):
        """ Detected column in 'Defects injected in Phase' plot (Fig.4-26 Left plot in Sweep manual)"""
        return np.sum(self.di_matrix, axis=0)

    @property
    def DDR(self):
        """ Detected col in 'Phase Injection' plot (Fig.4-26 Right plot in Sweep manual)"""
        return [self.di_matrix[i,i] for i in range(self.num_phases)]

    @property
    def L1(self):
        """ Initial estimate of defect latency (L1) """
        return [self.di_matrix[i,i]*self.leakage_rate for i in range(self.num_phases)]

    @property
    def I1(self):
        """ Initial estimate of defect injection (I1) per phase """
        return [np.sum(self.di_matrix[i,:]) + self.L1[i] for i in range(self.num_phases)]

    @property
    def I1T(self):
        """Total initial estimate of defects injected (I1T)"""
        return np.sum(self.I1)

    @property
    def RE1(self):
        """Initial relative error"""
        return 1 - (np.sum(self.L1) / self.latent_defects)

    #Intermediate computations------------------------------------------------------------------------------
    @property
    def AE(self):
        """Average Efficiency"""
        return 1 - self.leakage_rate

    @property
    def IEL(self):
        """Initial estimate of latency IEL"""
        return self.latent_defects - np.sum(self.L1)

    @property
    def DF(self):
        """Latent defects (DF) """
        return np.array(self.I1) - np.array(self.L1)

    @property
    def DR(self):
        """Defect rate per phase"""
        sumDF = np.sum(self.DF)
        return [d/sumDF for d in self.DF]

    @property
    def PLD(self):
        """Proportion of latent defects per phase (PLD)"""
        return [self.L1[i] + (self.DR[i] * self.IEL) for i in range(self.num_phases)]
    
    @property
    def ENID(self):
        """Estimated number of injected defects per phase"""
        return [self.DF[i] + self.PLD[i] for i in range(self.num_phases)]

    #Final Injection Calculations----------------------------------------------------------------------
    @property
    def I2(self):
        return [self.I1[i] + (self.DR[i] * self.IEL) for i in range(self.num_phases)]

    @property
    def L2(self):
        """Final estimate of defect latency per phase"""
        return [self.I2[i] - np.sum(self.di_matrix[i,:]) for i in range(self.num_phases)]

    @property
    def LEAK(self):
        """Leakage per phase"""
        return np.array(self.I2) - np.array(self.DDR)

    @property
    def LRATE(self):
        """Rate of leakage per phase"""
        return np.array(self.LEAK) / np.array(self.I2)

    #Updated Intermediate Calculations --------------------------------------------------------------------
    @property
    def UEL(self):
        """Updated estimate of latency"""
        return self.latent_defects - np.sum(self.L2)

    @property
    def UDF(self):
        """Updated total defects found"""
        return np.array(self.I2) - np.array(self.L2)
    
    @property
    def UDR(self):
        """Updated rate of defects found"""
        sumUDF = np.sum(self.UDF)
        return [udf/sumUDF for udf in self.UDF]

    @property
    def UPLD(self):
        """Updated proportion of latent defects per phase"""
        return np.array(self.L2) + (np.array(self.UDR) * self.UEL)

    @property
    def UENID(self):
        """Updated total estimated number of injected defects by phase"""
        return np.array(self.UDF) + np.array(self.UPLD)
    
    @property
    def RE2(self):
        """Number of relative errors """
        return 1 - (np.sum(self.L2) / self.latent_defects)

    #Quality Metrics---------------------------------------------------------------------------------------------------

    @property
    def LD(self):
        """Total number of latent defects"""
        return np.sum(self.L2)

    @property
    def ODDE(self):
        """Overall defect discovery Efficiency """
        sumUENID = np.sum(self.UENID)
        return (sumUENID - self.LD)/sumUENID

    @property
    def ADE(self):
        """Initial average discovery Efficiency"""
        return self.AE

    @property
    def EFC(self):
        """Defect detection Efficiency"""
        return [self.di_matrix[i,i]/self.I2[i] for i in range(self.num_phases)]

    @property
    def APDE(self):
        """Average phase defect discovery Efficiency"""
        return np.sum(self.EFC)/(self.num_phases - 1)

    @property
    def ADL(self):
        """Average defect leakage by phase"""
        return 1 - self.AE

    @property
    def LDPD(self):
        """latent defect as a percentage of total defects injected"""
        return 1 - self.ODDE
    
    @property
    def APDL(self):
        """Average phase defect leakage"""
        return 1 - self.APDE

    @property
    def TDI(self):
        """Total defects injected"""
        return np.sum(self.I2)

    @property
    def EFV(self):
        """Effectiveness of defect detection"""
        return [ self.efv_val(i) for i in range(self.num_phases)]

    def efv_val(self, i):
        if i == 0:
            return np.sum(self.di_matrix[:, i]) / (np.sum(self.I2[:i+1]))
        else:
            return np.sum(self.di_matrix[:, i]) / (np.sum(self.I2[:i+1]) - np.sum(self.di_matrix[:, :i]))

if __name__=="__main__":
    data = {}
    data['dp'] = [10.2, 6.32, 7.48, 6.27, 4.07, 2.11]
    data['ld'] = 1.32
    di = DefectInjection(data)
