import sys,os

import argparse
from math import *

import mbio.utils.utils as utils

def load_column(fname, col):
    data = []
    for line in open(fname):
        data.append(float(line.split()[col]))
    return data

def summary_column(fname, col):
    print_summary(load_column(fname, int(col)))


def show_hist(values):
    import matplotlib.pyplot as plt
    plt.hist(values, 120)
    # plt.xlabel("Minimum coverage")
    # plt.ylabel("Count")
    plt.show()

def hist_column(fname, col, area="0,100"):
    '''show histogram for one column'''
    import numpy as np
    col = int(col)
    area = [eval(i) for i in area.split(",")]
    print(area)
    assert len(area) == 2

    values = load_column(fname, int(col))

    values = sorted(values);
    low, median, high = np.percentile(values, area[0]), np.percentile(values, (area[0]+area[1])/2), np.percentile(values, area[1]);
    print("low, median, high", low, median, high)

    show_hist([i for i in values if i >= low and i <= high])

def hist_expr(fname, expr, condition="1"):
    values = []
    for line in open(fname):
        r = [eval(i) for i in line.split()]
        if eval(condition):  values.append(eval(expr))
    show_hist(values)


def load_col_items(fname, p):
    items = []
    for line in open(fname):
        its = line.split()
        items.append(its[p])
    return items

def tb_intersect(argv):
    '''表的两列元素的交集'''
    
    parser = argparse.ArgumentParser(tb_intersect.__doc__)
    parser.add_argument("table0", type=str)
    parser.add_argument("table1", type=str)
    parser.add_argument("--col0", type=int, default=0)
    parser.add_argument("--col1", type=int, default=0)
    try:
        args = parser.parse_args(argv)
        fname0 = sys.argv[2]
        fname1 = sys.argv[3]


        items0 = set(load_col_items(args.table0, args.col0))
        items1 = set(load_col_items(args.table1, args.col1))


        for i in items0 & items1:
            print(i)
    except:

        import traceback
        traceback.print_exc()
        print(tb_intersect.__doc__)


def tb_diff(argv):
    try:
        fname0 = sys.argv[2]
        fname1 = sys.argv[3]


        items0 = set(load_col_items(fname0, 0))
        items1 = set(load_col_items(fname1, 0))


        for i in items0 - items1:
            print(i)
    except:

        import traceback
        traceback.print_exc()
        print(tb_intersect.__doc__)
       



def sh_awk_mean():
    '''统计某列的平均值
    sh_awk_mean fname col
'''

    try:
        fname = "" if sys.argv[2] == '-' else sys.argv[2]
        col = int(sys.argv[3])

        cmd = "awk 'BEGIN {n=0;s=0} {n+=1; s+=$%d;} END{print(s/n)}' %s" % (col+1, fname)
        print(cmd)
        os.system(cmd)

    except:
        traceback.print_exc()
        print("----------------")
        print(sh_awk_mean.__doc__);



_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "tb_")


if __name__ == '__main__':
    main()

