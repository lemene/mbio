#

import numpy as np
import networkx as nx
import itertools
from collections import deque

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


F = -1*F

def create_graph(F):
    '''创建two-locus linkage graph
    :param F: numpy.array, SNPs矩阵 行表示flagment，列表示SNP，取值{-1,1,0}
    :return graph
    '''

    g = nx.Graph()

    for i,j in itertools.combinations(range(len(F[1,:])),2):  
        w = ((F[:,i]*F[:,j] == 1).sum(), (F[:,i]*F[:,j] == -1).sum())
        if w != (0, 0):
            g.add_edge(i, j, weight=w)

    return g


def delta0_gamma0(F):
    '''根据矩阵初始化delat、gamma参数'''

    c = (F == 1).sum() + (F == -1).sum() / len(F[0,:]) 

    # TODO delta和gamma的设定有疑问
    delta = 1
    gamma = min(0.5, max(0.1, delta/c))
    return (delta, gamma)

def label_graph(G, F):
    '''标注图节点'''

    block = 0
    delta0, gamma0 = delta0_gamma0(F)

    for n in G.nodes():
        if "label" not in G.node[n]:
            delta, gamma = delta0, gamma0

            while not label_component(G, n, delta, gamma):
                delta, gamma = delta+1, gamma + 0.1

            block += 1

    return block
            
        
def label_component(G, s, delta, gamma):
    '''标注error-tolerent component
    :param s: 标注的起点
    :returns: True表示标注了Component，False表示无法标注Component
    '''
    

    visited = {s: 1}

    queue = deque([s])

    while len(queue) > 0:
        ni = queue.popleft()
        for (ni, nj) in G.edges(ni):

            w = G.edge[ni][nj]["weight"]
            d = abs(w[0] - w[1])
            r = d/(w[0] + w[1])

            if d >= delta and r >= gamma:
                if nj not in visited:
                    queue.append(nj)
                    visited[nj] = (1 if w[0] > w[1] else -1) // visited[ni]
                else:
                    if w[0] > w[1] and visited[ni] != visited[nj] or w[0] <= w[1] and visited[ni] == visited[nj]:
                        return False

    for (k, v) in visited.items():
        G.node[k]["label"] = v
        G.node[k]["component"] = s
        print(k, s)

    return True



def contract_graph(G):
    '''将图的component合并成一个节点，要求label_graph'''
    cG = nx.Graph()
    cG.graph["old"] = G # 保留旧图

    cnodes = {}
    for gp in itertools.groupby(G.nodes(), lambda x: G.node[x]["component"]):
        if gp[0] not in cnodes: cnodes.setdefault(gp[0], [])
        cnodes[gp[0]].extend(list(gp[1]))

    for i,j in itertools.combinations(cnodes.values(), 2):
        wij = [0,0]
        for ni, nj in itertools.product(i, j):
            if G.has_edge(ni, nj):
                w = G.edge[ni][nj]["weight"]
                if G.node[ni]["label"] == G.node[nj]["label"]:
                    wij[0], wij[1] = wij[0]+w[0], wij[1]+w[1]
                else:
                    wij[0], wij[1] = wij[0]+w[1], wij[1]+w[0]
        if wij != [0,0]:
            cG.add_edge(frozenset(i), frozenset(j), weight=wij)

    return cG
    
def update_weight(G, F):
    if "old" not in G.graph:
        for i,j in G.edges():
            G.edge[i][j]["weight"] = ((F[:,i]*F[:,j] == 1).sum(), (F[:,i]*F[:,j] == -1).sum())
    else:
        update_weight(G.graph["old"], F)
        old = G.graph["old"]
        
        for i, j in G.edges():
            wij = [0, 0]
            for ni, nj in itertools.product(i, j):
                if old.has_edge(ni, nj):
                    w = old.edge[ni][nj]["weight"]
                    if old.node[ni]["label"] == old.node[nj]["label"]:
                        wij[0], wij[1] = wij[0]+w[0], wij[1]+w[1]
                    else:
                        wij[0], wij[1] = wij[0]+w[1], wij[1]+w[0]
            
            G.edge[i][j]["weight"] = wij

def correct_sequencing_error(G, F):

    change = False
    sub = get_labels(G)

    for l in sub.values():
        labels = np.zeros(len(F[0,:]))
        for k, v in l.items(): labels[k] = v 
       
        for f in F:
            s = labels * f
            s_0, s_1 = sum(s == -1), sum(s == 1)

            
            if s_0 != 0 and s_1 != 0 and s_0 != s_1:
                change |= True
                f[s == (1 if s_0 > s_1 else -1)] *= -1

        
    if change:
        update_weight(G, F)

    return change

def get_labels(G, n=None):    
    # 先计算几类label值
    def _get_labels(n, G):
        
        l = G.node[n].get("label", 1)

        if G.graph.get("old", None) != None:
            labels = {}
            for nn in n:
                labels.update(_get_labels(nn, G.graph["old"]))

            return {k: l*v  for k, v in labels.items()}

        else:
            return {n: l}

    if n == None:
        return {n: _get_labels(n, G) for n in G.nodes() }
    else:
        return {n: _get_labels(n, G)}


def haplotype(F):

    G = create_graph(F)
    print("create_graph")
    assert G.number_of_nodes() > 1
    change = True
    
    while change and G.number_of_nodes() > 1:
        label_graph(G, F)
        G = contract_graph(G)
        change = correct_sequencing_error(G, F)

    print([n for n in G.nodes()])
    return get_labels(G)



if __name__ == "__main__":
    print(haplotype(F))

