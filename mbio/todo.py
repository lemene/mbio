#! /usr/bin/env python3

'''存放没有归类的代码'''

import sys,os
import argparse
import matplotlib.pyplot as plt


import mbio.utils.utils as utils


def load_meryl_stat_file(fname):
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

def td_meryl_plot_frequency(argv):
    '''显示meryl statistics的频率分布'''
    
    parser = argparse.ArgumentParser(td_meryl_plot_frequency.__doc__)
    parser.add_argument("fnames", type=str, nargs='+')
    parser.add_argument("--range", type=tuple, default=(2,100))
    try:
        args = parser.parse_args(argv)
        [s, e] = args.range;
        for f in args.fnames:
            infos = load_meryl_stat_file(f)
            x = [i[0] for i in infos["details"]]
            y = [i[1] for i in infos["details"]]
            plt.plot(x[s:e], y[s:e])

        plt.show()
    except:
        import traceback
        traceback.print_exc()
        print("----------------")
        print(td_meryl_plot_frequency.__doc__)




_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "td_")

if __name__ == '__main__':
    main()
