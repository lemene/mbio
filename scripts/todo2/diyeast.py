import sys


POINT = 223005

def is_same_chromo(a0, a1):
    return a0 <= POINT and a1 <= POINT or a0 > POINT and a1 > POINT



def diy_get_ignored_ols():

    try:
        ifname = sys.argv[2]
        detail = bool(sys.argv[3]) if len(sys.argv) >= 4 else False

        ftype = "paf" if ifname.endswith("paf") else ""
        pos0, pos1 = (0, 5) if ftype == "paf" else (0, 1)

        count = [0, 0]
        for line in open(ifname):
            its = line.split()

            a0, a1 = int(its[pos0].split('_')[0]), int(its[pos1].split('_')[0])
            
            count[0] += 1
            if not is_same_chromo(a0, a1):
                count[1] += 1
                if detail: print(line, end="")

        if not detail: print(count, count[1]/count[0])
    except:
        import traceback
        traceback.print_exc()
        print(diy_get_ignored_ols.__doc__)


def diy_check_ignored():
    '''根据标准分割线，ignore文件的错误和遗漏'''
    
    try:
        ignfname = sys.argv[2]
        ovlpfname = sys.argv[3] if len(sys.argv) >= 4 else ""
        ftype = "paf" if ovlpfname.endswith("paf") else ""
        pos0, pos1 = (0, 5) if ftype == "paf" else (0, 1)
        

        
        ignored = set()

        for line in open(ignfname):
            its = [int(i) for i in line.split()]

            if len(its) >= 2:
                for i in its[1:]:
                    ignored.add((min(its[0], i), max(its[0], i)))

        count = [0, 0]
        for i in ignored:
            count[0] += 1
            if is_same_chromo(i[0],i[1]):
                count[1] += 1

        print(count, 1-count[1]/count[0])
        if ovlpfname != "":
            count = [0, 0, 0, 0]
            for line in open(ovlpfname):
                its = line.split()

                a0, a1 = int(its[pos0].split('_')[0]), int(its[pos1].split('_')[0])

                iid = (min(a0, a1), max(a0, a1))
                if is_same_chromo(a0, a1):
                    if iid in ignored:
                        count[0] += 1
                    else:
                        count[1] += 1
                else:
                    if iid in ignored:
                        count[2] += 1
                    else:
                        count[3] += 1


            print(count)

    except:
        import traceback
        traceback.print_exc()
        print(diy_get_ignored_ols.__doc__)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
       locals()[sys.argv[1]]()
    else:
       for func in list(locals().keys()):
           if func.startswith("diy_"):
               print(func)
