import numpy

class Stats(object):
    def __init__(self, shape):
        self._n = 0
        self._x = numpy.zeros(shape)##, dtype=double)
        self._xx = numpy.zeros(shape)##, dtype=double)
        self._xy = numpy.zeros(shape)##, dtype=double)

    def mean(self):
        return self._x/self._n

    def rms(self):
        return ((self._xx/self._n - (self._x/self._n)**2)).clip(0)**0.5

    def corr(self, yMean, ySigma):
##        return (self._xy -self._x*yMean)/self._n
        if ySigma >0:
            rmsPosDef = self.rms().clip(0.000001, self.rms().max())
            return numpy.double((self._xy -self._x*yMean)/(self._n*ySigma*rmsPosDef))
        else:
            return None

    def accumulate(self, x, y=0):
        self._n += 1
        self._x += x
        self._xx += x*x
        self._xy += x*y

    
if __name__ == '__main__':
    a = numpy.zeros([10])
    s = Stats(a.shape)
    for i in range(10000):
        d = numpy.sin((numpy.array(list(range(10)))+i)/3.14159)
        s.accumulate(d, d[7])

    print(s.mean())
    print(s.rms())
    print(s.corr(s.mean()[7], s.rms()[7]))
