class CapitalBudgeting:
    '''
    indicators for capital budgeting
    '''
    def __init__(self, cfs: list[float]):
        '''
        cfs: list of cash flows, including initial investment
        '''
        self.cfs = cfs
        self.irregular = len(list(filter(lambda cf: cf < 0, self.cfs))) > 1
    def npv(self, rate: float, start0: bool = True) -> float:
        '''
        net present value, regular or irregular cash flows
        Parameters:
        - rate: discounted rate
        - start0: is cfs include initial investment? MS Excel's npv() start0 = False
        Returns: float
        Example
        from capitalbudgeting import CapitalBudgeting as CapBud
        cfs = [-100, 21, 21, 24, 23, 32, 25]
        cb = CapBud(cfs)
        cb.npv(0.09)
        '''
        s = 0.0
        for t, cf in enumerate(self.cfs):
            if start0:
                s += cf / (1 + rate) ** t
            else:
                s += cf / (1 + rate) ** (t + 1)
        return s
    def __irr2(self, niter: int = 100) -> float:
        '''
        internal rate of return for regular cash flows only
        Parameters
        - niter: number of iteration
        Returns: float
        Example:
        from capitalbudgeting import CapitalBudgeting as CapBud
        cfs = [-100, 21, 21, 24, 23, 32, 25]
        cb = CapBud(cfs)
        cb._CapBud__irr2()        
        '''
        if sum(self.cfs) < 0:
            raise Exception('insufficient cash flows')
        rate = 1.0
        invest = self.cfs[0]
        for i in range(1, niter + 1):
            rate *= (1 - self.npv(rate) / invest)
        return rate
    def irr(self, maxinter: int = 1000, guess: tuple[float] = None, tolerance = 1.0e-7) -> float:
        '''
        internal rate of return for regular or irregular cash flows with bisection method
        Parameters
        - maxiter: maximum number of iteration
        - guess: scope to look for solution, e.g. (0.05, 0.07)
        Returns: float
        Example:
        from capitalbudgeting import CapitalBudgeting as CapBud
        cfs = [-80, 21, 21, -25, 30, 25, 25]
        cb = CapBud(cfs)
        cb.irr()  
        '''
        if not self.irregular:
            return self.__irr2(maxinter)
        else:
            if guess is None:
                raise Exception('guess should not be None for irregular cash flows')
            else:
                a = guess[0]
                b = guess[1]
                m = (a + b) / 2
                if self.npv(a) * self.npv(b) > 0:
                    raise Exception('no solution within the scope guess')
                iter = 0 
                while iter < maxinter:
                    if abs(self.npv(m)) <= tolerance:
                        return m
                    else:
                        if (self.npv(a)) * (self.npv(m)) > 0:
                            a = m
                        else:
                            b = m
                        m = (a + b) / 2
                        iter += 1
                raise Exception(f'can not get solution after {iter} iteration')
    def mirr(self, reinvestrate: float, financerate: float = None) -> float:
        '''
        modified internal rate of return for regular or irregular cash flows
        Parameter
        - reinvestrate: reinvestment rate for positive cash flows
        - financerate: interest rate for investment (negative cash flows). for irregular cfs, financerate can NOT be None 
        Return: float
        Example
        from capitalbudgeting import CapitalBudgeting as CapBud
        cfs = [-80, 21, 21, -25, 30, 25, 25]
        cb = CapBud(cfs)
        cb.mirr(0.06, 0.09)
        '''
        if self.irregular and (financerate is None):
            raise Exception('financerate for irregular cash flows should not be None')
        pcfs = [cf if cf > 0 else 0.0 for cf in self.cfs]
        ncfs = [-cf if cf < 0 else 0.0 for cf in self.cfs]
        n = len(self.cfs) - 1   # exclude basis period
        fvpcfs = [cf * (1 + reinvestrate) ** (n - t) for (t, cf) in enumerate(pcfs)]
        if self.irregular:
            pvncfs = [cf / (1 + financerate) ** t for (t, cf) in enumerate(ncfs)]
        else:
            pvncfs = [-self.cfs[0]]
        return (sum(fvpcfs) / sum(pvncfs)) ** (1 / n) - 1
    def ipp(self) -> float:
        '''
        investment payback period
        Parameters
        Returns: float
        Example:
        from capitalbudgeting import CapitalBudgeting as CapBud
        cfs = [-100, 21, 21, 24, 23, 32, 25]
        cb = CapBud(cfs)
        cb.ipp()
        '''
        if sum(self.cfs) < 0:
            raise Exception("insufficient cash flows")
        s, i, ccf = self.cfs[0], 1, [self.cfs[0]]
        while s < 0.0:
            s += self.cfs[i]
            ccf.append(s)
            i += 1
        n = len(ccf)
        return n - 2 - ccf[n - 2] / self.cfs[n - 1]
