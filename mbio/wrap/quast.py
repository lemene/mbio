#! /usr/bin/env python3

from pydoc import describe
import sys, os
import traceback
import argparse
from collections import defaultdict
import glob

import mbio.utils.utils as utils

def quast_get_misassembly(argv):
    '''获得quast检测的组装错误'''
    parser = argparse.ArgumentParser(quast_get_misassembly.__doc__)
    parser.add_argument("qwrkdir", type=str, help="quast的输出目录")

    try:
        args = parser.parse_args(argv)
        all_mis = []

        tsvfname = glob.glob(f"{args.qwrkdir}/contigs_reports/all_alignments_*.tsv")[0]

        pairs = []
        for lineno, line in enumerate(open(tsvfname)):
            if lineno == 0: continue

            if line.startswith("CONTIG"):
                its = line.split()
                ctg_name, ctg_len = its[1], int(its[2])
                
                if len(pairs) == 0: continue

                if len(pairs[-1].split()) <= 6:
                    pairs.pop()
                assert len(pairs) % 2 == 1

                for i, p in enumerate(pairs):
                    if i % 2 == 0:
                        p = p.split()
                        assert p[5] == its[1] 
                        assert int(p[2]) >= 1 and int(p[2]) <= ctg_len 
                        assert int(p[3]) >= 1 and int(p[3]) <= ctg_len 
                
                pp = pairs[0].split()
                s = min( int(pp[2]), int(pp[3]))
                if s >= 1000:
                    all_mis.append((pp[5], 1, s, "translocation"))


                for j in range(0, len(pairs)-2):
                    
                    type = pairs[j+1].split(',')[0]
                    if type in set(["relocation", "local misassembly", "inversion", "translocation"]):
                        its0 = pairs[j].split()
                        its2 = pairs[j+2].split()
                        assert its0[5] == its2[5]
                        s0, e0 = int(its0[2]), int(its0[3])
                        s2, e2 = int(its2[2]), int(its2[3])
                        pos = sorted((s0, e0, s2, e2))
                        all_mis.append((its0[5], pos[1], pos[2], type))

                pp = pairs[-1].split()
                e = max( int(pp[2]), int(pp[3]))
                if ctg_len -e >= 1000:
                    all_mis.append((pp[5], e, ctg_len, "translocation"))

                pairs = []
            else:
                pairs.append(line.strip())

        all_mis.sort()

        for mis in all_mis:
            print("%s %d %d \"%s\"" % (mis[0],mis[1], mis[2], mis[3]))

    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()

_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "quast_")

if __name__ == '__main__':
    main()
