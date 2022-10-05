import sys
import matplotlib.pyplot as plt
import traceback
import argparse
import random


def qp_line():
    '''以线段方式显示文件某一列数据
    qp_line fname col
'''
    try:
        fname = sys.argv[2]
        col = int(sys.argv[3])
        data = []
        y = []
        for i, line in enumerate(open(fname)):
            data.append(float(line.split()[col]))
            #y.append(i*0.01 - 1)
            y.append(i)
        plt.plot(y, data)
        plt.show()
    except:
        traceback.print_exc()
        print(qp_line.__doc__)

def load_column(fname, col):
    data = []
    for line in open(fname):
        data.append(float(line.split()[col]))
    return data

def show_hist(values):
    plt.hist(values, 200)
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

    values = sorted(values)
    low, median, high = np.percentile(values, area[0]), np.percentile(values, (area[0]+area[1])/2), np.percentile(values, area[1]);
    print("low, median, high", low, median, high)

    show_hist([i for i in values if i >= low and i <= high])

def qp_hist():
    '''show histogram for one column'''

    fname = sys.argv[2]
    col = int(sys.argv[3])
    area = "0,100" if len(sys.argv) < 5 else sys.argv[4]
    area = [eval(i) for i in area.split(",")]
    print(area)
    assert len(area) == 2


    import numpy as np

    values = load_column(fname, int(col))

    values = sorted(values);
    low, median, high = np.percentile(values, area[0]), np.percentile(values, (area[0]+area[1])/2), np.percentile(values, area[1]);
    print("low, median, high", low, median, high)

    show_hist([i for i in values if i >= low and i <= high])

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
    
def qp_test():
    def func(a, b, *args, k=True):
        print(a, b, k)

    func(1,2,2)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
       locals()[sys.argv[1]]()
    else:
       for func in list(locals().keys()):
           if func.startswith("qp_"):
               print(func)
