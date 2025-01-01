#! /usr/bin/env python3

from pydoc import describe
import sys, os
import traceback
import argparse
from collections import defaultdict

import mbio.utils.utils as utils
import mbio.utils.logger as logger
import matplotlib.pyplot as plt

complemented_base = {'A':'T', 'C': 'G', 'G':'C', 'T':'A'}
def reverse_complemented(seq):
    rcseq = [complemented_base[i] for i in seq]
    return ''.join(rcseq[::-1])




def load_stat_file(fname):
    '''加载meryl statistics生成的文件'''

    infos = {}
    infos["details"] = []

    for i, line in enumerate(open(fname)):
        if i >= 11:
            its = line.split()
            assert len(its) == 5
            x = int(its[0]), int(its[1]), float(its[2]), float(its[3]), float(its[4])
            infos["details"].append(x)

    return infos

def meryl_plot_frequency(argv):
    '''显示meryl statistics的频率分布'''
    
    
    parser = argparse.ArgumentParser(meryl_plot_frequency.__doc__)
    parser.add_argument("fnames", type=str, nargs='+')
    parser.add_argument("--range", type=lambda s: tuple(int(n) for n in s.split(',')), default="2,100")
    try:
        args = parser.parse_args(argv)
        print(range)
        [s, e] = args.range;
        for f in args.fnames:
            infos = load_stat_file(f)
            x = [i[0] for i in infos["details"]]
            y = [i[1] for i in infos["details"]]
            plt.plot(x[s:e], y[s:e], label=f)
        plt.legend()
        plt.show()
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(meryl_plot_frequency.__doc__)




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

def meryl_kmer_type(argv):
    '''检查kmer是否是meryl的类型，参考meryl_adjust_order
'''
    parser = argparse.ArgumentParser(meryl_adjust_order.__doc__)
    parser.add_argument("ifname", type=str, default="-")

    try:
        args = parser.parse_args(argv)
        kmers = set()
        for line in utils.open_readable_file(args.ifname):
            its = line.split()      # ACGT    3
            if its[0] in kmers or reverse_complemented(its[0]) in kmers:
                print("meryl")
                break
            else:
                kmers.add(its[0])
        else:
            print("ok")
    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()

_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "merly_")

if __name__ == '__main__':
    main()
