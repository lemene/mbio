#! /usr/bin/env python3

from pydoc import describe
import sys, os
import traceback
import argparse
import glob
import multiprocessing as mp
from collections import defaultdict
import logging

import mbio.utils.utils as utils
import mbio.utils.logger as logger

complemented_base = {'A':'T', 'C': 'G', 'G':'C', 'T':'A'}
def reverse_complemented(seq):
    rcseq = [complemented_base[i] for i in seq]
    return ''.join(rcseq[::-1])


def meryl_adjust_order(argv):
    '''调整meryl print 输出的kmer。meryl采用ACTG顺序，而不是通常意义ACGT顺序。
https://meryl.readthedocs.io/en/latest/reference.html
'''
    parser = argparse.ArgumentParser(meryl_adjust_order.__doc__)
    parser.add_argument("ifname", type=str, default="-")
    parser.add_argument("ofname", type=str, default="-")

    try:
        args = parser.parse_args(argv)

        with utils.open_writeable_file(args.ofname) as of:
            for line in utils.open_readable_file(args.ifname):
                its = line.split()      # ACGT    3
                its[0] = min(its[0], reverse_complemented(its[0]))
                of.write("%s\n" % ("\t".join(its)))
    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()



_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "merly_")

if __name__ == '__main__':
    main()
