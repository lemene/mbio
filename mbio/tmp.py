#! /usr/bin/env python3

'''存放尚未分类的脚本'''
from collections import defaultdict
import sys, os
import traceback
import argparse
import math

prjdir = os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), ".."])
sys.path.append(prjdir)

import mbio.utils.utils as utils
import mbio.utils.logger as logger
from mbio.fsa.misc import *

import numpy as np


# from sklearn.cluster import AgglomerativeClustering
# import numpy as np
 
# agglom = AgglomerativeClustering(n_clusters=3)  # 定义层次聚类算法，分3个簇
# agglom.fit(data)  # 用数据训练算法
# labels = agglom.labels_  # 获取每个样本的簇标签

#from sklearn.cluster import DBSCAN

def kmean(data):
    data.sort()
    lw, hg = data[0] + (data[-1]-data[0])/4, data[0] + (data[-1]-data[0])*3/4, 

    mid = (lw + hg) / 2

    while True:
        lset, hset = list(), list()
        for d in data:
            if abs(d - lw) < abs(d-hg):
                lset.append(d)
            else:
                hset.append(d)

                
        lw = sum(lset) / len(lset)
        hg = sum(hset) / len(hset)

        if abs(lw + hg - 2*mid) < 0.00001:
            break
        else:
            mid = (lw + hg) / 2

    return lset, hset, mid

def cluster(data, bins, INV):
    data.sort()
    mid = data[len(data)//2]
    b_mid = math.ceil((mid + 1) / INV )
    lw = np.argmax(bins[0:b_mid]) * INV - 1
    hg = (np.argmax(bins[b_mid:])+b_mid) * INV - 1
    
    print(lw, hg)
    print(bins)
    mid = (lw + hg) / 2
    while True:
        lset, hset = list(), list()
        for d in data:
            if abs(d - lw) < abs(d-hg):
                lset.append(d)
            else:
                hset.append(d)

                
        lw = sum(lset) / len(lset)
        hg = sum(hset) / len(hset)

        if abs(lw + hg - 2*mid) < 0.00001:
            break
        else:
            mid = (lw + hg) / 2

    
    return lset, hset, mid

import itertools
def distance(data):
    ss = 0
    for d0, d1 in itertools.combinations(data, 2):
        ss += abs(d0 - d1)
    return ss

def distance2(data0, data1):
    ss = 0
    
    for d0, d1 in itertools.product(data0, data1):
        ss += abs(d0 - d1)
    return ss

def density(data):
    return len(data)/(max(data)-min(data))


def calc_density(bins):
    k = 5
    dd = []
    dd.append(sum(bins[:k]))
    for i in range(k+1, len(bins)):
        dd.append(dd[-1] + bins[i] - bins[i-k-1])

    print("xxx", dd)


def tmp_group_infos(argv):
    
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser(tmp_count_kmer.__doc__)
    parser.add_argument("infos", type=str)
    try:
        best_map = {}

        args = parser.parse_args(argv)
        scores = [float(line.split()[-2]) for line in open(args.infos)]
 
        scores.sort()
        INV = 0.01
        bins = [0] * (math.ceil(2 / INV) + 1)
        print(len(bins))
        for s in scores:
            n = math.ceil((s + 1.0) / INV)
            bins[n] += 1

        calc_density(bins)
        
        dst = scores
        while True:
            lset, hset, mid = cluster(dst, bins, INV)
            print(len(hset), mid, distance(dst), distance(lset), distance(hset), distance2(lset, hset))
            print("density", density(lset), density(hset), density(scores))
            dst = hset
            break


        #lset, hset, mid = kmean(hset)
        #lset, hset, mid = kmean(hset)
        labels = [0 if s < mid else 1 for s in scores]

        # agglom = AgglomerativeClustering(n_clusters=8)  # 定义层次聚类算法，分3个簇
        # agglom.fit(np.array(scores).reshape([len(scores),1]))  # 用数据训练算法
        # labels = agglom.labels_  # 获取每个样本的簇标签
        print(labels)
        plt.scatter(list(range(len(scores))), scores, c=labels)
        plt.title('Hierarchical Clustering')
        plt.show()
        assert 0
        # 查看聚类结果
        bins = [0] * 201
        for s in scores:
            n = math.ceil((s + 1.0) / 0.01)
            bins[n] += 1

        def smooth(s, k):
            ss = [0]*(len(s) - k + 1)
            ss[0] = sum(s[0:k])
            for i in range(k+1, len(s)):
                ss[i-k] = ss[i-k-1] + s[i] - s[i-k-1]
            return [i/k for i in ss]
            return ss
            
        sbins = smooth(bins, 100)
        print(bins)
        print(sbins)
        plt.plot(list(range(len(sbins))),sbins)
        plt.show()
            
    except:
        traceback.print_exc()

def tmp_filter_paf(argv):
    parser = argparse.ArgumentParser(tmp_count_kmer.__doc__)
    parser.add_argument("detail", type=str)
    parser.add_argument("read", type=str)
    parser.add_argument("paf", type=str)
    try:
        best_map = {}

        args = parser.parse_args(argv)
        for line in open(args.detail):
            its = line.split()
            c,rr = its[-1].split(":")
            s, e = rr.split("-")
            best_map[its[0]] = (c, int(s), int(e))

        reads = set()
        assert args.read in best_map
        ctg, start, end = best_map[args.read]
        for rd, (c, s, e) in best_map.items():
            if ctg == c and e >= start and s <= end:
                reads.add(rd)
        
        for line in open(args.paf):
            its = line.split()
            if its[0] in reads and its[5] in reads:
                print(line, end="")
    except:
        traceback.print_exc()

def tmp_detail(argv):
    parser = argparse.ArgumentParser(tmp_count_kmer.__doc__)
    parser.add_argument("detail", type=str)
    parser.add_argument("--read", type=str)
    parser.add_argument("--bed", type=str, default="")
    parser.add_argument("--olsize", type=int, default=5000)
    
    try:
        best_map = {}

        args = parser.parse_args(argv)
        for line in open(args.detail):
            its = line.split()
            c,rr = its[-1].split(":")
            s, e = rr.split("-")
            best_map[its[0]] = (c, int(s), int(e))


        if args.bed:
            ctg, rr = args.bed.split(":")
            [start, end] = [int(r) for r in rr.split("-")]
        else:
            assert args.read in best_map
            ctg, start, end = best_map[args.read]
        for rd, (c, s, e) in best_map.items():
            if ctg == c and e >= start and s <= end and min(e, end) - max(s, start) >= args.olsize:
                print(rd, min(e, end) - max(s, start))
    except:
        traceback.print_exc()

def tmp_cmp_detail(argv):
    '''比较两个fsa_ol_tools accuracy 生成的detail文件'''
    parser = argparse.ArgumentParser(tmp_cmp_detail.__doc__)
    parser.add_argument("detail0", type=str)
    parser.add_argument("detail1", type=str)
    try:
        args = parser.parse_args(argv)

        def load_detail(fname):
            infos = {}
            for line in open(fname):
                its = line.split()
                infos[its[0]] = its

            return infos

        detail0 = load_detail(args.detail0)
        detail1 = load_detail(args.detail1)

        diff = []
        for k, v in detail0.items():
            if k not in detail1:
                #diff.append([0, v])
                pass
            else:
                v1 = detail1[k]
                diff.append([(float(v[8]) - float(v1[8])), v, v1])

        diff.sort(key=lambda x: -x[0])

        for i in diff:
            print(i)


    except:
        traceback.print_exc()

def tmp_count_kmer(argv):
    '''计算每条读数的kmer。'''
    parser = argparse.ArgumentParser(tmp_count_kmer.__doc__)
    parser.add_argument("detail", type=str)
    parser.add_argument("read", type=str)
    parser.add_argument("-k", type=int, default=19)
    try:
        args = parser.parse_args(argv)
        import pysam

        pass


    except:
        traceback.print_exc()

def tmp_position_in_reference(argv):
    """计算read的起点在reference的位置"""
    parser = argparse.ArgumentParser(tmp_position_in_reference.__doc__)
    parser.add_argument("paf", type=str)
    try:
        args = parser.parse_args(argv)
        for line in open(args.paf):
            its = line.split()
            if its[4] == '+':
                print(its[0], its[5], int(its[7]) - int(its[2]))
            else:
                print(its[0], its[5], int(its[8]) + int(its[2]))
    except:
        traceback.print_exc()

def tmp_check_overlap(argv):
    """使用read在reference的位置检查overlap是否正确"""
    parser = argparse.ArgumentParser(tmp_check_overlap.__doc__)
    parser.add_argument("paf", type=str)
    parser.add_argument("position", type=str)
    parser.add_argument("--tile", type=str, default="")
    try:
        args = parser.parse_args(argv) # x l s e + x l s e
        positions = {}
        for line in open(args.position):
            its = line.split()
            positions[its[0]] = (its[1], int(its[2]))

        pairs = set()
        if len(args.tile) > 0:
            ctgs = PrjFile.get_contig_reads(args.tile)
            for ctg, reads in ctgs.items():
                for rd0, rd1 in zip(reads[:-1], reads[1:]):
                    if rd0 < rd1:
                        pairs.add((rd0, rd1))
                    else:
                        pairs.add((rd1, rd0))


        for line in open(args.paf):
            its = line.split()
            s0, e0, s1, e1 = int(its[2]), int(its[3]), int(its[7]), int(its[8])
            off = 0
            if its[4] == '+':
                off = abs(s0 - s1)
            else:
                off = s0 + s1 + (e0 - s0 + e1 - s1) / 2

            if its[0] in positions and its[5] in positions and \
                (len(pairs) == 0 or (its[0], its[5]) in pairs or (its[5], its[1]) in pairs):
                if positions[its[0]][0] == positions[its[5]][0] and \
                    abs(abs(positions[its[0]][1] - positions[its[5]][1]) - off) < 500:
                    pass
                else:
                    #print(line, end="")
                    print(positions[its[0]], its[0], positions[its[5]], its[5])

    except:
        traceback.print_exc()



_local_func = locals()
def main():
    utils.script_entry(sys.argv, _local_func, "tmp_")


if __name__ == '__main__':
    main()



