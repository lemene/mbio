#! /usr/bin/env python3

import sys,os
import re
import threading
import queue
import multiprocessing

CIGAR_PATTERN = re.compile(r"(\d+)([MIDNSHP=X])")

def is_paf_ok(its, max_oh):
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

def stat_cigar(qs, qe, ql, d, ts, te, tl, cigar, ref):

    toff = ts
    size, clip, match, insert, delete, mismatch, hclip = ql, 0, 0, 0, 0, 0, 0
    if d == '+':
        clip += min(qs,ts)
        clip += min(ql-qe, tl-te)
    else:
        clip += min(ts, ql-qe)
        clip += min(qs, tl-te)
    hclip = qs + ql - qe

    for m in CIGAR_PATTERN.finditer(cigar):
        n, p = int(m.group(1)), m.group(2)

        if p == "=":
            match += n

            for i in range(n): ref[toff+i] += 1
            toff += n

        elif p == "X":
            mismatch += n

            toff += n

        elif p == 'I':
            insert += n
        elif p == 'D':
            delete += n
            toff += n

        else:   # p in 'SHM':
            assert False, "不支持cigar的%s" % p

    assert toff == te
    return size, clip, match, insert, delete, mismatch, hclip

def stat_lines(lines):
    reads = {}
    coverage = {}
    for line in lines:
        its = line.split()

        for i in its[12:]:
            if i.startswith("cg:Z:"):
                cigar = i[5:]

        if its[5] not in coverage:
            coverage[its[5]] = [0]*int(its[6])
    
        r = stat_cigar(int(its[2]), int(its[3]), int(its[1]), its[4], int(its[7]), int(its[8]), int(its[6]), cigar, coverage[its[5]])
        
        if its[0] not in reads or reads[its[0]][2] < r[2]:
            reads[its[0]] = r

    return reads, coverage

def stat_file(fname, N):
    #reads, coverage = stat_lines(open(ifname).readlines())

    lines = open(fname).readlines();

    if len(lines) < N:
        N = 1
        block = len(lines)
    else:
        block = (len(lines) + N - 1) // N;
    print(N, block)
    p = multiprocessing.Pool(processes=N)
    result = [p.apply_async(stat_lines, args=(lines[i*block:(i+1)*block],)) for i in range(N)]

    reads = {}
    coverage = {}
    for res in result:
        (r, c) = res.get();

        for k, v in r.items():
            if k not in reads or reads[k][2] < v[2]:
                reads[k] = v;

        for k, v in c.items():
            if k not in coverage:
                coverage[k] = v
            else:
                assert len(coverage[k]) == len(v)
                for i, iv in enumerate(v):
                    coverage[k][i] += iv;

    return reads, coverage
def print_stat_info(reads):
    size, clip, match, insert, delete, mismatch, hclip = 0, 0, 0, 0, 0, 0, 0
    for k, v in reads.items():
        size += v[0]
        clip += v[1]
        match += v[2]
        insert += v[3]
        delete += v[4]
        mismatch += v[5]
        hclip += v[6]

    size_gap = size+delete
    print("     size: %d" % size)
    print(" accuracy: %.06f" % (match/(size_gap-hclip)))
    print("    match: %.06f" % (match/size_gap))
    print(" mismatch: %.06f" % (mismatch/size_gap))
    print("insertion: %.06f" % (insert/size_gap))
    print(" deletion: %.06f" % (delete/size_gap))
    print("     clip: %.06f" % (clip/size_gap))
    print("    hclip: %.06f" % (hclip/size_gap))

def print_info_detail(reads):
    for k, v in reads.items():
        print(k, v[2]/(v[0]+v[4]), v[0], v[1], v[2], v[3], v[4], v[5], v[6])

def print_cov_info(coverage):
    all_cov = [0, 0]
    for n, cov in coverage.items():
        l, c = len(cov), sum([c > 0 for c in cov])
        all_cov[0] += l
        all_cov[1] += c
        #print(n, l/c)
    print(" fraction: %.06f" % (all_cov[1]/all_cov[0]))

def paf_accuracy2():
    try:
        ifname = sys.argv[2]

        reads, coverage = stat_lines(open(ifname).readlines())
        print_stat_info(reads)
        print_cov_info(coverage)
    except:
        import traceback
        traceback.print_exc()
        print(paf_accuracy.__doc__)

def paf_test():
    '''输出统计最大的前n条overlap'''
    try:
        ifname = sys.argv[2]
        itype = "mismatch" if len(sys.argv) < 4 else sys.argv[3]
        num = 5 if len(sys.argv) < 5 else int (sys.argv[4])

        pos = {"clip":1, "match":2, "insert":3, "delete":4, "mismatch":5, "hclip":6 }[itype]
        result = [[None, [-1,-1,-1,-1,-1,-1, -1]] for i in range(num)]

        reads, coverage = stat_file(ifname, 10)

        maxclip = [None, [0,-1,0,0,0, 0]]
        err_clips = []
        size, clip, match, insert, delete, mismatch = 0, 0, 0, 0, 0, 0
        for k, v in reads.items():
            size += v[0]
            clip += v[1]
            match += v[2]
            insert += v[3]
            delete += v[4]
            mismatch += v[5]

            if result[0][1][pos] < v[pos]:
                result[0] = [k, v]
                result.sort(key=lambda x: x[1][pos])

        for k, v in result:
            print(k, v)
    except:
        import traceback
        traceback.print_exc()
        print(paf_accuracy.__doc__)


def paf_accuracy(argv):
    try:
        ifname = argv[0]
        N = 10  if len(argv) < 2 else int(argv[1])

        reads, coverage = stat_file(ifname, N)
        print(len(coverage))
        print_stat_info(reads)
        print_cov_info(coverage)
    except:
        import traceback
        traceback.print_exc()
        print(paf_accuracy.__doc__)

def paf_detail_accuracy(argv):
    try:
        ifname = argv[0]
        N = 10  if len(argv) < 2 else int(argv[1])

        reads, coverage = stat_file(ifname, N)
        print(len(coverage))
        print_info_detail(reads)
    except:
        import traceback
        traceback.print_exc()
        print(paf_detail_accuracy.__doc__)

def paf_mecat_detail_accuracy():
    try:
        ifname = sys.argv[2]
        ifmap = sys.argv[3]
        N = 10  if len(sys.argv) < 5 else int(sys.argv[4])

        name = [i.strip() for i in open(ifmap)]

        reads, coverage = stat_file(ifname, N)
        for k, v in reads.items():
            n = name[int(k.split("_")[0])]            
            print(n, v[2]/(v[0]+v[4]), v[0], v[1], v[2], v[3], v[4], v[5], v[6])
    except:
        import traceback
        traceback.print_exc()
        print(paf_mecat_detail_accuracy.__doc__)


def paf_fsa_detail_accuracy():
    try:
        ifname = sys.argv[2]
        ifmap = sys.argv[3]
        N = 10  if len(sys.argv) < 5 else int(sys.argv[4])

        name = {}
        for i in open(ifmap):
            its = i.split()
            name[its[0]] = name[1]
 
        reads, coverage = stat_file(ifname, N)
        for k, v in reads.items():
            n = name[k]            
            print(n, v[2]/(v[0]+v[4]), v[0], v[1], v[2], v[3], v[4], v[5], v[6])
    except:
        import traceback
        traceback.print_exc()
        print(paf_fsa_detail_accuracy.__doc__)

def paf_filter(argv):
    try:
        ifname = argv[0]
        oh = int (argv[1])
        reads = {}
        for line in open(ifname):
            its = line.split()
            if is_paf_ok(its, oh):
                print(line, end="")
            
    except:
        import traceback
        traceback.print_exc()
        print(paf_accuracy.__doc__)

def paf_readnames():
    '''获取overlaps的reads名称'''
    try:
        ifname = sys.argv[2]

        tick = [0, 1000]
        size = [0,os.path.getsize(ifname)]

        percent = lambda x: x[0]/x[1]

        names = set()
        for line in open(ifname):
            its = line.split()
            names.add(its[0])
            names.add(its[5])

            size[0] += len(line)
            if percent(size) > percent(tick):
                print("\r%f" % percent(size), file=sys.stderr, end="")
                tick[0] += 1

        print("\r%f" % 1, file=sys.stderr)
        for n in names: print(n)
    except:
        import traceback
        traceback.print_exc()
        print(paf_readnames.__doc__)

def paf_coverage(argv):
    '''获取overlaps的reads名称'''
    try:
        ifname = argv[0]
        name = argv[1]
        stub = 0 if len(argv) < 3 else int(argv[2])

        ranges = []

        for line in open(ifname):
            its = line.split()
            if its[0] == name:
                ranges.append((int(its[2]), int(its[3])))
            elif its[5] == name:
                ranges.append((int(its[7]), int(its[8])))
                
        size = max([r[1] for r in ranges])
        cov = [0]*(size+1)

        for r in ranges:
            if r[1] - r[0] <= 2*stub: continue
            cov[r[0]+stub] += 1
            cov[r[1]-stub] -= 1

        for i in range(1, len(cov)):
            cov[i] += cov[i-1]

        for c in cov: print(c)
    except:
        import traceback
        traceback.print_exc()
        print(paf_coverage.__doc__)


def paf_m4_coverage(argv):
    '''获取overlaps的reads名称'''
    try:
        ifname = argv[0]
        name = argv[1]
        stub = 0 if len(argv) < 3 else int(argv[2])

        ranges = []

        for line in open(ifname):
            its = line.split()
            if its[0] == name:
                ranges.append((int(its[5]), int(its[6])))
            elif its[1] == name:
                ranges.append((int(its[9]), int(its[10])))
                
        size = max([r[1] for r in ranges])
        cov = [0]*(size+1)

        for r in ranges:
            if r[1] - r[0] <= 2*stub: continue
            cov[r[0]+stub] += 1
            cov[r[1]-stub] -= 1

        for i in range(1, len(cov)):
            cov[i] += cov[i-1]

        for c in cov: print(c)
    except:
        import traceback
        traceback.print_exc()
        print(paf_coverage.__doc__)


def paf_center():
    '''提取相关的overlap
    paf_extract fname name [level=1]
'''
    try:
        ifname = sys.argv[2]
        name = sys.argv[3]
        level = 1 if len(sys.argv) < 5 else int(sys.argv[4])

        names = set([name])
        for i in range(level):
            level_names = set()
            for line in open(ifname):
                its = line.split()
                if its[0]  in names:
                    level_names.add(its[5])
                elif its[5] in names:
                    level_names.add(its[0])
                else:
                    pass
            names.update(level_names)

        for line in open(ifname):
            its = line.split()
            if its[0] in names or its[5] in names:
                print(line, end="")

    except:
        import traceback
        traceback.print_exc()
        print(paf_coverage.__doc__)

def paf_stat_cigar(argv):
    try:
        fname = argv[0]

        for line in open(fname):
            its = line.split()

            for i in its[12:]:
                if i.startswith("cg:Z:"):
                    cigar = i[5:]
                    toff, qoff = (0, 0)
                    distance = 0;
                    tprint = 0
                    for m in CIGAR_PATTERN.finditer(cigar):
                        n, p = int(m.group(1)), m.group(2)

                        if p == "=":
                            toff += n

                        elif p == "X":
                            distance += n

                            toff += n

                        elif p == 'I':
                            distance += n
                        elif p == 'D':
                            distance += n
                            toff += n

                        else:   # p in 'SHM':
                            assert False, "不支持cigar的%s" % p

                        if toff - tprint >= 500:
                            print("[%d,%d], %d, %d, %f" % (tprint, toff, toff-tprint, distance, distance / (toff-tprint)))
                            tprint=toff
                            distance = 0

    except:
        import traceback
        traceback.print_exc()
        print(paf_coverage.__doc__)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
       locals()[sys.argv[1]](sys.argv[2:])
    else:
       for func in list(locals().keys()):
           if func.startswith("paf_"):
               print(func)
