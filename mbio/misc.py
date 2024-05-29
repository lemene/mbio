#! /usr/bin/env python3

'''存放尚未分类的脚本'''
from asyncore import read
from collections import defaultdict
import sys, os
import traceback
import argparse

prjdir = os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), ".."])
sys.path.append(prjdir)

import utils
from logger import logger

        
def misc_read_in_genome(argv):
    '''获取read比对上的genome序列片段。'''
    parser = argparse.ArgumentParser(misc_read_in_genome.__doc__)
    parser.add_argument("read", type=str)
    parser.add_argument("genome", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("--wrkdir", type=str, default="__wrkdir__")
    try:
        args = parser.parse_args(argv)

        os.system("mkdir -p %s" % args.wrkdir)

        tmppaf = os.path.join(args.wrkdir, "tmp.paf")
        cmd = "minimap2 %s %s -c > %s" % (args.genome, args.read, tmppaf)
        utils.run(cmd)

        ctgs = defaultdict(list)
        for line in open(tmppaf):
            its = line.split()
            ctgs[its[5]].append((int(its[7]), int(its[8])))
            
        ctgitems = sorted(list(ctgs.items()), key=lambda x: -len(x[1]))
        rs = [min([i[0] for i in ctgitems[0][1]]), max([i[1] for i in ctgitems[0][1]])]
        ctg = ctgitems[0][0]
        logger.info("get %s[%d,%d)" % (ctg, rs[0], rs[1]))
        tmpfasta = os.path.join(args.wrkdir, "tmp.fasta")
        cmd = "~/work/fsa/build/bin/fsa_rd_tools sub %s %s --names %s" % (args.genome, tmpfasta, ctg)
        utils.run(cmd)

        with open(args.output, "w") as ofile:
            f = open(tmpfasta)
            l = f.readline()
            print(l, end="")
            ofile.write(l)
            l = f.readline()
            ofile.write(l[rs[0]:rs[1]])


    except:
        traceback.print_exc()
        print("----------------")
        print(misc_read_in_genome.__doc__)


if __name__ == '__main__':
    utils.script_entry(sys.argv, locals(), "misc_")



