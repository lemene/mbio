
import mbio.io.csv as mcsv
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
        index = [i for i, cv in enumerate(matrix.transpose()) if ttest(filter(cv, lvalue[0]), filter(cv, lvalue[1]), 10, alpha)]
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
        for mi in m:
            if mi != -1: 
                all_value.append(mi)

    cap = np.percentile(all_value, 99)
    capIpds = np.minimum(all_value, cap)
    m = capIpds.mean()

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i,j] != -1:
                matrix[i,j] /= m
    
    print(cap)
    print(matrix)
    return matrix

def normalize(matrix, label):
    matrix = norm1(matrix)
    all_value = []
    for m in matrix:
        for mi in m:
            if mi != -1: 
                all_value.append(mi)

    cap = np.percentile(all_value, 99)

    print(cap)

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


def test_feature(csvfile, mark, alpha):
    matrix, label, row, col = mcsv.load_matrix(csvfile)
    omatrix = matrix.copy()

    itrain, itest = random_split_data(0.8, matrix, label)
    matrix = normalize(matrix, label)

    labeltype = { l:i for i, l in enumerate(sorted(set([l for l in label if mark in l]))) }

    assert "left" == mark or "right" == mark and len(labeltype) == 2
        
    lvalue = list(labeltype.keys())
    
    itest_all = ttest_matrix(matrix, label, lvalue, alpha)
    itest_train = ttest_matrix(omatrix[itrain,], label[itrain], lvalue, alpha)
 
    print(itest_all)
    print(itest_train)

def ttest_matrix(matrix, label, lvalue, alpha):
    def filter(x, l, label): 
        xl = x[label == l]
        return xl[xl!=-1]
    return [i for i, cv in enumerate(matrix.transpose()) if ttest(filter(cv, lvalue[0], label), filter(cv, lvalue[1], label), 10, alpha)]

if __name__ == "__main__":
    import sys
    #show_all_ipd(sys.argv[1], "right", 0.03)
    test_feature(sys.argv[1], "right", 0.03)