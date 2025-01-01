import sys,os

import argparse
import traceback
#import matplotlib.pyplot as plt
from math import *
import random
import matplotlib.pyplot as plt

import mbio.utils.utils as utils
import mbio.utils.logger as logger

def load_column(fname, col):
    data = []
    for line in open(fname):
        data.append(float(line.split()[col]))
    return data 

def show_hist(values):
    plt.hist(values, 100)
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



def tb_line(argv):
    '''以线段方式显示文件某一列数据
'''
    
    parser = argparse.ArgumentParser(tb_line.__doc__)
    parser.add_argument("fname", type=str)
    parser.add_argument("col", type=int, default=0)
    try:
        args = parser.parse_args(argv)

        data = []
        y = []
        for i, line in enumerate(open(args.fname)):
            data.append(float(line.split()[args.col]))
            y.append(i)
        plt.plot(y, data)
        plt.show()
    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()

def tb_hist(argv):
    '''show histogram for one column'''

    
    parser = argparse.ArgumentParser(tb_line.__doc__)
    parser.add_argument("fname", type=str)
    parser.add_argument("col", type=int, default=0)
    parser.add_argument("--low", type=int, default=0)
    parser.add_argument("--high", type=int, default=100)
    try:
        args = parser.parse_args(argv)

        import numpy as np
        import matplotlib.pyplot as plt

        values = load_column(args.fname, args.col)

        values.sort()
        low, median, high = np.percentile(values, args.low), np.percentile(values, (args.low+args.high)/2), np.percentile(values, args.high);
        print("low, median, high", low, median, high)

        show_hist([i for i in values if i >= low and i <= high])
    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()

def qp_scatter():
    ifname = sys.argv[2]
    pos = [0] if len(sys.argv) < 4 else [int(i) for i in sys.argv[3].split(",")]

    x, y = [], []
    for line in open(ifname):
        its = line.split()
        x.append(int(its[pos[0]]))
        if len(pos) > 1:
            y.append(int(its[pos[1]]))
        else:
            y.append(0+ random.random())
    plt.scatter(x, y, s=1)
    plt.ylim([-5, 5])
    plt.show()
    
def tb_sort(argv):
    '''根据第几列排序，默认从大到小'''
    parser = argparse.ArgumentParser(tb_sort.__doc__)
    parser.add_argument("fname", type=str)
    parser.add_argument("col", type=int, default=0)
    parser.add_argument("--line", type=int, default=5)
    parser.add_argument("--rev", type=int, default=5)
    parser.add_argument("--low", type=float, default=-10000000000)
    parser.add_argument("--high", type=float, default=10000000000)
    try:
        args = parser.parse_args(argv)
        data = []
        for i, line in enumerate(open(args.fname)):
            its = line.split()
            v = float(its[args.col])
            if v >= args.low and v <= args.high:
                data.append((float(its[args.col]), line, i))

        data.sort(key=lambda i: -i[0])

        for i, d in enumerate(data):
            if i < args.line:
                print(d[1], end="")
            else:
                break

    except:
        traceback.print_exc()
        print("-----------------")
        parser.print_usage()


_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "tb_")


if __name__ == '__main__':
    main()

