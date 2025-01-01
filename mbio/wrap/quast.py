#! /usr/bin/env python3

from pydoc import describe
import sys, os
import traceback
import argparse
from collections import defaultdict

import mbio.utils.utils as utils

def quast_get_misassembly(argv):
    '''获得quast检测的组装错误'''
    parser = argparse.ArgumentParser(quast_get_misassembly.__doc__)
    parser.add_argument("qwrkdir", type=str, help="quast的输出目录")

    try:
        args = parser.parse_args(argv)
        all_mis = []

        types = set(["relocation", "local misassembly", "inversion", "translocation"])
        mis = [None]*4
        for i, line in enumerate(open(f"{args.qwrkdir}/contigs_reports/all_alignments_simu_asm.tsv")):
            if i == 0: continue

            if i % 2 == 1:
                its = line.split()
                mis[0] = its[5]
                mis[1] = int(its[1])
                mis[2] = int(its[3])

            else:
                mis[3] = line.strip().split(',')[0]
                if mis[3] in types:
                    all_mis.append(mis) 
                mis = [None]*4

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
