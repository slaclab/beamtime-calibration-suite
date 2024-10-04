import argparse
import sys, os

parser = argparse.ArgumentParser(
    description="Configures calibration suite, overriding experimentHash",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--r0", type=int, help="first run")
parser.add_argument("--r1", type=int, help="second run")
parser.add_argument("--exp0", type=str, help="first experiment")
parser.add_argument("--exp1", type=str, default='', help="second experiment, defaults to first")
parser.add_argument("-d", type=str, help="epixm, epixhr, ... - compare detnames")

args = parser.parse_args()

##print(args)
exp0 = args.exp0
exp1 = args.exp1
if args.exp1 == '':
    exp1 = exp0


f0 = "/tmp/file_%s_r%d.txt" %( exp0, args.r0)
f1 = "/tmp/file_%s_r%d.txt" %( exp1, args.r1)
fdiff = "/tmp/fdiff.txt"
print("see files", f0, f1, fdiff)

os.system("config_dump exp=%s,run=%d %s raw > /tmp/f0.txt" %(exp0, args.r0, args.d))
os.system("config_dump exp=%s,run=%d %shw config >> /tmp/f0.txt" %(exp0, args.r0, args.d))
os.system("sort /tmp/f0.txt > %s"%(f0))

os.system("config_dump exp=%s,run=%d %s raw > /tmp/f1.txt" %(exp1, args.r1, args.d))
os.system("config_dump exp=%s,run=%d %shw config >> /tmp/f1.txt" %(exp1, args.r1, args.d))
os.system("sort /tmp/f1.txt > %s"%(f1))

os.system("diff %s %s > %s" %(f0, f1, fdiff))
os.system("cat %s" %(fdiff))
