
from math import *

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


if __name__ == "__main__":
    import sys
    locals()[sys.argv[1]](*sys.argv[2:])
