import numpy
import logging
logger = logging.getLogger(__name__)

class Cluster(object):
    def __init__(self, row, col, energy):
        self.seedCol = col
        self.seedRow = row
        self.seedEnergy = energy
        self.nPixels = 0
        self.nMaskedPixels = 0
        self.eTotal = 0
        self.eTotalNoCuts = 0
        self.eSecondaryPixelNoCuts = 0
        self.goodCluster = True
        self.clusterSide = 3
        self.pixelE = numpy.zeros((self.clusterSide, self.clusterSide))
        
        self.addPixel(0, 0, energy)
        self.eTotalNoCuts += energy

    def addPixel(self, offsetR, offsetC, energy):
        self.nPixels += 1
        if (energy>self.seedEnergy): self.goodCluster = False
        self.eTotal += energy
        self.pixelE[offsetR+1, offsetC+1] = energy ## pixel seed in 1, 1; corner in -1, -1; etc.
        
    def blindlyNoteEnergy(self, energy):
        self.eTotalNoCuts += energy
        ## add to pixel list or array or something
        if (energy>self.eSecondaryPixelNoCuts): self.eSecondaryPixelNoCuts = energy

    def centroid(self):
        weightedC = 0
        weightedR = 0
    
        for i in range(3):
            for j in range(3):
                weightedR += self.pixelE[i, j]*(i+0.5)
                weightedC += self.pixelE[i, j]*(j+0.5)
        c = weightedC/self.eTotal - 1.5 + self.seedCol
        r = weightedR/self.eTotal - 1.5 + self.seedRow
        return (r, c)

    def isSquare(self):
        if (self.nPixels==1): return True
        if (self.nPixels==2):
            if (self.pixelE[0, 0]!=0 or
                self.pixelE[0, 2]!=0 or 
                self.pixelE[2, 0]!=0 or 
                self.pixelE[2, 2]!=0): return False
            return True
        if (self.nPixels<5):
            rowSum0 = (self.pixelE[0, 0]==0) and (self.pixelE[0, 1]==0) and (self.pixelE[0, 2]==0)
            rowSum2 = (self.pixelE[2, 0]==0) and (self.pixelE[2, 1]==0) and (self.pixelE[2, 2]==0)
            colSum0 = (self.pixelE[0, 0]==0) and (self.pixelE[1, 0]==0) and (self.pixelE[2, 0]==0)
            colSum2 = (self.pixelE[0, 2]==0) and (self.pixelE[1, 2]==0) and (self.pixelE[2, 2]==0)
            ## could demand no corner energy for 3-pixel clusters
            if ((rowSum0 or rowSum2) and (colSum0 or colSum2)): return True
        return False

    def maskedNeighbor(self):
        self.nMaskedPixels += 1


class BuildClusters(object):
    def __init__(self, frame, seedCut, neighborCut):
        self.frame = frame
        self.seedCut = seedCut
        self.neighborCut = neighborCut

    def findClusters(self):
        clusters = []
        rows, cols = self.frame.shape
        for r in range(1, rows-1):
            for c in range(1, cols-1):
                if self.frame[r, c]<self.seedCut:
                    continue
                cluster = Cluster(r, c, self.frame[r, c])
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if (i==0 and j==0): continue;
                        en = self.frame[r+i, c+j];
                        cluster.blindlyNoteEnergy( en)
                        if en>self.neighborCut:
                            cluster.addPixel(i, j, en)
                if cluster.goodCluster:
                    clusters.append(cluster)
        return clusters

