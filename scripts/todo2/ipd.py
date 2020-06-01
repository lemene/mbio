
import mbio.io.csv as mcsv

import mbio.io.csv as mcsv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import numpy as np
from scipy.stats import ttest_ind
import pdb


cm = plt.get_cmap('jet')
cNorm  = colors.Normalize(vmin=0, vmax=5-1)
scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)

def ttest(y0, y1, size, alpha):
    if len(y0) >= size and len(y1) >= size: 
        return ttest_ind(y0, y1, equal_var=False)[1] < alpha
    else:
        return False

def show_all_ipd(csvfile, mark="", alpha=1):
    matrix, label, row, col = mcsv.load_matrix(csvfile)


    labeltype = { l:i for i, l in enumerate(sorted(set([l for l in label if mark in l]))) }
    x = [[] for t in labeltype]
    y = [[] for t in labeltype]

    if "left" == mark or "right" == mark and len(labeltype) == 2:
        lvalue = list(labeltype.keys())
        def filter(x, l): 
            xl = x[label == l]
            return xl[xl!=-1]
        index = [i for i, cv in enumerate(matrix.transpose()) if ttest(filter(cv, lvalue[0]), filter(cv, lvalue[1]), 2, alpha)]
    else:
        index = list(range(len(col)))

    for m, l, r in zip(matrix[:,index], label, row):
        for mi, c in zip(m, col[index]):
            if mi >= 0 and l in labeltype:
                x[labeltype[l]].append(c)
                y[labeltype[l]].append(mi)

    for i, (xi, yi) in enumerate(zip(x, y)):
        li = plt.scatter(xi, yi, color=scalarMap.to_rgba(i), s=3)
        print(i, scalarMap.to_rgba(i))

    
    plt.show()



def random_split_data(ratio, matrix, label):
    nraw, ncol = matrix.shape
    types = set(label)

    index = []
    for t in types:

        tindex = [i for i, l in enumerate(label) if l == t]
        sample = np.random.choice(tindex, int(ratio*len(tindex)), replace=False)

        index.extend(sample)

    #count = int(nraw*ratio)
    #index = np.random.choice(range(nraw), count, replace=False)
    
    return np.array(index), np.array([i for i in range(nraw) if i not in index])

def norm1(matrix):
    all_value = []
    for m in matrix:
        all_value.append(m[m!=-1])

    all_value = np.hstack(all_value)

    cap = np.percentile(all_value, 99)
    capIpds = np.minimum(all_value, cap)
    m = capIpds.mean()

    for i in range(len(matrix)):
        matrix[i, matrix[i,:]!=-1] /= m
    
    #print(cap)
    #print(matrix)
    return matrix

def normalize(matrix, label):
    matrix = norm1(matrix)
    all_value = []
    for m in matrix:
        for mi in m:
            if mi != -1: 
                all_value.append(mi)

    cap = np.percentile(all_value, 99)

    #print(cap)

    labeltype = set(label)
    mm = matrix.copy()
    for i, mc in enumerate(matrix.transpose()):

        for lt in labeltype:
            row = mc[label == lt]
            if len(row) > 2:
                percentile = min(90, (1.0- 1.0/(len(row)-1))*100)
                lcap = np.percentile(row, percentile)
                capValue = max(cap, lcap)
                #row = np.minimum(row, capValue)

                mm[label==lt, i] = np.minimum(mm[label==lt, i], capValue)


    return mm


def test_feature(csvfile, mark, ratio, alpha, count=1):
    alpha = float (alpha)
    ratio = float(ratio)
    count = int(count)

    matrix, label, row, col = mcsv.load_matrix(csvfile)
    omatrix = matrix.copy()

    jaccard, train_size, all_size, train_in_all = 0, [], [], 0
    for i in range(count):
        itrain, itest = random_split_data(ratio, matrix, label)
        #  matrix = normalize(matrix, label)
        matrix = norm1(matrix)
        labeltype = { l:i for i, l in enumerate(sorted(set([l for l in label if mark in l]))) }

        assert "left" == mark or "right" == mark and len(labeltype) == 2
        
        lvalue = list(labeltype.keys())
    
        Q = alpha
        itest_all = set(np.array(range(matrix.shape[1]))[benjamini_hochberg_filter(matrix, label==lvalue[0], label==lvalue[1], Q)])
        itest_train =  set(np.array(range(matrix[itrain,].shape[1]))[benjamini_hochberg_filter(matrix[itrain,], label[itrain,]==lvalue[0], label[itrain,]==lvalue[1], Q)])
        #itest_all = set(ttest_matrix(matrix, label, lvalue, alpha))
        #itest_train = set(ttest_matrix(matrix[itrain,], label[itrain], lvalue, alpha))

        #print(itest_all)
        #print(itest_train)

        train_size.append(len(itest_train))
        all_size.append(len(itest_all))

        train_in_all += len(itest_train.intersection(itest_all)) / len(itest_all)

        jaccard += len(itest_all.intersection(itest_train)) / len(itest_all.union(itest_train))
    print(train_size)
    print("Size:", all_size[0], np.mean(train_size), np.var(train_size))
    print("Jaccard index:", jaccard/count, train_in_all/count)
 

def ttest_matrix(matrix, label, lvalue, alpha):
    def filter(x, l, label): 
        xl = x[label == l]
        return xl[xl!=-1]
    return [i for i, cv in enumerate(matrix.transpose()) if ttest(filter(cv, lvalue[0], label), filter(cv, lvalue[1], label), 10, alpha)]


def benjamini_hochberg_filter(matrix, type1, type2, Q):
    def test_value(cls0, cls1, size=5):
        if len(cls0) < size or len(cls1) < size:
            return 1
        return ttest_ind(cls0, cls1, equal_var=True)[1]

    pvalues = [test_value(c[type1][c[type1]!=-1], c[type2][c[type2]!=-1]) for c in matrix.transpose()]
    count = sum([1 for p in pvalues if p < 1])

    sortarg = sorted(range(len(pvalues)), key=lambda x: pvalues[x], reverse=True)

    for i, s in enumerate(sortarg[len(sortarg)//2:]):
        i += len(sortarg)//2
        if pvalues[s] < (len(sortarg) - i) / count * Q:
            break
            

    return [ e in sortarg[i:] for e in range(len(sortarg))]

def summary_matrix(csvfile):
    from collections import defaultdict
    matrix, label, row, col = mcsv.load_matrix(csvfile)
    print("matrix.shape:", matrix.shape)

    labelcount = defaultdict(int)
    for l in label: labelcount[l] += 1

    print("Label Count:", labelcount.items())

    readcount = defaultdict(int)
    for r in row: readcount[r] += 1

    countread = defaultdict(list)
    for r, c in readcount.items():
        countread[c].append(r)
        
    for c, r in countread.items():
        print(c, len(r))
        if c >= 4: print(r)

    

if __name__ == "__main__":
    import sys
    locals()[sys.argv[1]](*sys.argv[2:]) 