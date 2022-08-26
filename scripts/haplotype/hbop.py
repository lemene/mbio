import numpy as np
from collections import deque
import itertools
from functools import reduce

F = np.array([
    [ 1, -1,  0,  0,  0,  0],
    [ 1,  0, -1,  0,  0,  0],
    [ 1, -1, -1,  0,  0,  0],
    [-1,  1,  1,  0,  0,  0],
    [-1, -1,  1,  0, -1,  0],
    [ 0,  1, -1,  1,  0,  0],
    [ 0, -1,  1,  1,  0,  0],
    [ 0,  0,  0, -1,  1,  0],
    [ 0,  0,  0,  1, -1,  0],
    [ 0,  0,  0, -1,  1,  0],
    [ 0,  0,  0,  1,  1,  1]])




def fragments_cut(F, P1, P2):
    return sum([(F[i,:] * F[j,:]).sum() for i, j in itertools.product(P1, P2)])
       

def error_correction(H, F):
    return sum([min((H * f == -1).sum(), ((H*-1)*f == -1).sum()) for f in F])

def balanced_optimal_partition(F, P1, P2, w):
    return error_correction(partition_to_haplotype(F, P1, P2), F) - w*fragments_cut(F, P1, P2)

def partition_to_haplotype(F, P1, P2=None):
    '''根据分区确定haplotype的值
    :param F: flagments再各个snp点的值
    :param P1, P2: 
    '''


    P2 = P2 if P2 != None else set(range(len(F))).difference(P1)
    
    a = sum([F[i,:]*1 == 1 for i in P1]) + sum([F[i,:]*-1 == 1 for i in P2])
    b = sum([F[i,:]*-1 == 1 for i in P1]) + sum([F[i,:]*1 == 1 for i in P2])
    H = np.ones(len(F[0,:]))
    H[b-a>0] = -1
    return H


def sort_snp_matrix(F):
    '''排序snp矩阵每行首末非零元素的位置排序'''
    borders = [np.nonzero(f)[0][np.array([0,-1])] for f in F]

    orders = sorted(range(len(borders)), key=lambda x: (borders[x][0],borders[x][1]))

    nF = np.zeros(F.shape)
    for i,j in zip(range(len(nF)), orders): nF[i,:] = F[j,:]

    return nF



def haplotype(F, w):

    F = sort_snp_matrix(F)
    borders = [np.nonzero(f)[0][np.array([0,-1])] for f in F]

    H, R = [(0, set()), (0, set([0]))], set([0])

    for i in range(1, len(F)):
        print(i)
        
        Rc = set([r for r in R if borders[i][0] <= borders[r][1]])

        H1 = {frozenset(k): max(v) for k, v in itertools.groupby(H, lambda x:Rc.intersection(x[1]))}

        R = Rc.union([i])
        H.clear()
        for k, v in H1.items():
            P1, P2 = v[1], set(range(i)).difference(v[1])
            h = partition_to_haplotype(F, P1, P2)
            H.append((error_correction(h, F), P1))

            P1 = v[1].union(set([i]))
            P2 = set(range(i)).difference(P1)
            h = partition_to_haplotype(F, P1, P2)
            H.append((error_correction(h, F), P1))


    
    H = sorted(H, key=lambda x: x[0])
    print(H[0:4])
    Hs = H[3]
    print(partition_to_haplotype(F, Hs[1], set(range(len(F))).difference(Hs[1]))) 
if __name__ == "__main__":
    haplotype(F, 0.1)
