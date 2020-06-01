import sys

def is_paf_ok(its):
    max_oh = 200
    if int(its[10]) < 2000: 
        return False

    if its[4] == '+':
        if int(its[2]) > max_oh and int(its[7]) > max_oh:
            return False
        if int(its[1]) - int(its[3]) > max_oh and int(its[6]) - int(its[8]) > max_oh:
            return False
    else:
        if int(its[2]) > max_oh and int(its[6]) - int(its[8]) > max_oh:
            return False
        if int(its[1]) - int(its[3]) > max_oh and int(its[7]) > max_oh:
            return False
        
    return True 
def cluser(ifname, ofname, locs, ids):
    ids = set(ids)
    reserve = []
    for line in open(ifname):
        its = line.split()
        if not is_paf_ok(its):
            continue
        k = False
        for loc in locs:
            if its[loc] in ids:
                k = True
        if k:
            reserve.append(line)
            [ids.add(its[loc]) for loc in locs]

    ofile = open(ofname, "w")
    for line in reserve:
        ofile.write(line)


def ol_cluster():
    if len(sys.argv) == 6:
        ifname, ofname = sys.argv[2:4]
        locs = [int(l) for l in sys.argv[4].split(",")]
        ids = sys.argv[5].split(",")

        cluser(ifname, ofname, locs, ids)
        
    else:
        print("ol_cluster ifname ofname loc[,loc] id[,id,...]")



if __name__ == "__main__":
    if len(sys.argv) > 1:
       locals()[sys.argv[1]]()
    else:
       for func in list(locals().keys()):
           if func.startswith("ol_"):
               print(func)