#! /usr/bin/env python3

import sys, os
import traceback

prjdir = os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), ".."])
sys.path.append(prjdir)

import mbio.io.fastq as fastq

def misc_kbm2paf(argv):
    '''将wtdbg2的kbm2生成的比对数据转化成paf
    tl_kbm2paf kbm paf [reads]
'''
    try:
        
        kbm = argv[0]
        paf = argv[1]
        reads = argv[2] if len(argv) >= 3 else ""

        lens = {}
        if reads != "":
            for head, seq in fastq.Iterator(reads):
                lens[head[0]] = str(len(seq))


        ofile = open(paf, "w")
        for line in open(kbm):
            its = line.split()
            if len(lens) > 0:
                paf_item = [its[0], lens[its[0]], its[3], its[4], "+" if its[1] == its[6] else "-", its[5], lens[its[5]], its[8], its[9], its[10], its[11], "60\n"]
            else:
                paf_item = [its[0], its[2], its[3], its[4], "+" if its[1] == its[6] else "-", its[5], its[7], its[8], its[9], its[10], its[11], "60\n"]
            ofile.write("\t".join(paf_item))
    except:
        traceback.print_exc()
        print("----------------")
        print(misc_kbm2paf.__doc__)


def misc_params(argv):
    '''一些有用的参数组合'''

    try:
        params = {
            "quast-large": "--min-contig 5000 --large --min-identity 90",
            "quast-large-fragment": "--min-contig 5000 --large --min-identity 90 --fragmented"
        }
        if len(argv) == 0:
            print(params)
        else:
            print(params[argv[0]])


    except:
        traceback.print_exc()
        print("----------------")
        print(misc_params.__doc__)

        
if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]](sys.argv[2:])
    else:
       for func in list(locals().keys()):
           if func.startswith("misc_"):
               print("%s: %s" % (func, locals()[func].__doc__.split("\n")[0]))



