import sys

c0 = open(sys.argv[1], "r")
c1 = open(sys.argv[2], "r")

lines0 = c0.readlines()
lines1 = c1.readlines()

for l0 in lines0:
    if not l0.startswith("config"):
        continue
    if l0.startswith("step 1"):
        break
    try:
        r0, v0 = l0.split()
    except:
        ##        print(l0)
        continue

    for l1 in lines1:
        if not l1.startswith("config"):
            continue
        if l1.startswith("step 1"):
            break
        try:
            r1, v1 = l1.split()
        except:
            continue
        if r1 == r0 and v1 != v0:
            print("%s: %s -> %s" % (r0, v0, v1))
