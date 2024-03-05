import sys, os, glob
from subprocess import call

basePath = sys.argv[1]
baseRun = sys.argv[2]
analysisType = sys.argv[3]
runs = sys.argv[4].split(",")
try:
    label = "_" + sys.argv[5]
except:
    label = ""

command = "python AnalyzeH5.py -r %s -f " % (baseRun)
for r in runs:
    globString = "%s/%s*r%s*.h5" % (basePath, analysisType, r)
    f = glob.glob(globString)
    try:
        command += f[-1] + ","
    except:
        print("could not find %s" % (globString))

command = command[:-1]
print(command)
