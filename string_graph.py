import networkx as nx
from functools import reduce

class StringGraph(object):
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_overlap(self, a, alen, abpos, aepos, b, blen, bbpos, bepos):
        assert alen >= aepos and aepos >= abpos and abpos >= 0

        if abpos > 0 and  bbpos < bepos:
            """
                -------->       a
                    -------->   b
            """
            self.graph.add_edge((a,'E'), (b, 'E'), length=blen-bepos)
            self.graph.add_edge((b,'B'), (a, 'B'), length=abpos)
        elif abpos > 0 and bbpos >= bepos:            
            """
                -------->       a
                    <--------   b
            """
            self.graph.add_edge((a,'E'), (b, 'B'), length=bepos)
            self.graph.add_edge((b,'E'), (a, 'B'), length=abpos)

        elif abpos == 0 and bbpos < bepos:
            """
                    -------->   a
                -------->       b
            """
            self.graph.add_edge((a,'B'), (b,'B'), length=bbpos)
            self.graph.add_edge((b,'E'), (a,'E'), length=alen-aepos)
        else:
            assert abpos == 0 and bbpos >= bepos
            """
                    -------->   a
                <--------       b
            """
            self.graph.add_edge((a,'B'), (b, 'E'), length=blen-bbpos)
            self.graph.add_edge((b,'B'), (a, 'E'), length=alen-aepos)


    def transitive3(self):
        print(len(self.graph.edges()))
        for v in self.graph.nodes():
            mark = { e[1]: "inplay" for e in self.graph.out_edges(v) }

            for w in mark:
                for e in self.graph.out_edges(w):
                    print("--", e)
                    if mark.get(e[1], "none") == "inplay":
                        diff = self.graph.edge[v][e[1]]["length"] - (self.graph.edge[w][e[1]]["length"] + self.graph.edge[v][w]["length"])
                        if -10 < diff and diff <10:
                            print(v, e[1])
                            self.graph.remove_edge(v,e[1])

            
        print(len(self.graph.edges()))


def simple_transitive(g, FUZZ):

    print(g.number_of_edges())
    
    reduce = { e : False for e in g.edges() }

    for v in g.nodes():
        mark = { w: "inplay" for v,w in g.out_edges(v) }

        for w in mark:
            for w, x in g.out_edges(w):
                if mark.get(x, "none") == "inplay":
                    diff = g.edge[v][x]["length"] - (g.edge[w][x]["length"] + g.edge[v][w]["length"])
                    if -FUZZ < diff and diff <FUZZ:
                        mark[x] = "eliminated"
                        reduce[(v,x)] = True
                        #reduce[(w,x)] = True


    [g.remove_edge(*e) for e, v in reduce.items() if v]
    print(g.number_of_edges())

def standard_transitive(g, FUZZ):
    '''Myers 1995 Transitive reduction algorithm'''

    print(g.number_of_edges())

    mark = { v: "vacant" for v in g.nodes() }
    reduce = { e : False for e in g.edges() }

    for v in g.nodes():
        out_edges = g.out_edges(v)
        if len(out_edges) == 0: continue

        for v,w in out_edges: mark[w] = "inplay" 

        out_edges.sort(key=lambda x: g.edge[x[0]][x[1]]["length"])

        longest =  g.edge[out_edges[-1][0]][out_edges[-1][1]]["length"] + FUZZ

        for v, w in out_edges:  # TODO 论文没有说明顺序
            if mark[w] == "inplay":
                for w, x in g.out_edges(w):
                    if mark[x] == "inplay" and g.edge[w][x]["length"] + g.edge[v][w]["length"] <= longest:
                        mark[x] = "eliminated"

        for v, w in out_edges:
            w_outs = g.out_edges(w)
            if len(w_outs) == 0: continue

            w_outs.sort(key=lambda x: g.edge[x[0]][x[1]]["length"])
            
            if mark[w_outs[0][1]] == "inplay": mark[w_outs[0][1]] = "eliminated"
            
            for w, x in w_outs[1:]:
                if g.edge[w][x]["length"] < FUZZ and mark[x] == "inplay":
                    mark[x] = "eliminated"

        for v, w in out_edges:
            if mark[w] == "eliminated":
                reduce[(v,w)] = True
            mark[w] = "vacant"

    [g.remove_edge(*e) for e, v in reduce.items() if v]
    print(g.number_of_edges())



def test_overlap():
    import lasfile
    import matplotlib.pyplot as plt
    import forceatlas2
    import random

    las = lasfile.LasFile(r".\NCTC11022\rawreads.rawreads.S.las", lasfile.DBFile(r".\NCTC11022\rawreads"))
    
    sg = StringGraph()
    for s in las:
        sg.add_overlap(*s)  

    simple_transitive(sg.graph, 10)

    #nx.draw(sg.graph)
    #plt.show()
    return


    G = sg.graph.to_undirected()
    pos = { i : (random.random(), random.random()) for i in G.nodes()} 
    l = forceatlas2.forceatlas2_networkx_layout(G, pos, niter=100)
    nx.draw_networkx(G, l, with_labels=False,cmap = 'hsv',vmin = 0, node_size=8,linewidths=0.1) 
    plt.savefig("a.png")
    plt.show()


   #for ovlp in las.overlaps:
   #    print(ovlp.path.abpos, ovlp.path.aepos, ovlp.path.bbpos, ovlp.path.bepos)

import networkx as nx



def connect_strand(g):
    '''将string_graph的平行的点建立边，使得图像布局时两个点合成一个点'''
    for n in g.nodes():
        if n[-1] == 'E' or n[-1] == 'B' and g.has_node(n[:-1]+'B') and g.has_node(n[:-1]+'E'):
            
            g.add_edge(n[:-1]+'E', n[:-1]+'B')
            g.add_edge(n[:-1]+'B', n[:-1]+'E')

    return g

def load_falcon_graph(sg_edges_list):
    '''加载falcon产生的图，一般是sg_edges_list文件
    它记录了边信息，各列的意义参考其它文件
    '''
    
    g = nx.DiGraph()
    with open(sg_edges_list) as f:
        for line in f:
            e = line.strip().split()
            if e[7] == 'G': 
                g.add_edge(e[0], e[1], attr=e)  # TODO 属性可以更精细

    return g



def set_colors(H):
    '''为每个点上色，'''
    color_map = { n : -1 for n in H.nodes() }

    color_index = 5
    for n in color_map:
        if color_map[n] == -1:
            (c, color_index) = (color_index, color_index+1)

            color_map[n] = c

            curr = n
            outs = H.out_edges(curr)

            # forward
            while len(outs) == 1 or (len(outs) == 2 and (outs[0][::-1] in H.edges() or outs[1][::-1] in H.edges())):

                next = outs[0][1]
                if len(outs) == 2 and (next, curr) in H.edges():
                    color_map[next] = c
                    next = outs[1][1]
                elif len(outs) == 2:
                    color_map[outs[1][1]] = c

                if color_map[next] == -1:
                    color_map[next] = c
                    curr = next
                    outs = H.out_edges(curr)
                else:
                    break
        
            # backward
            curr = n
            ins = H.in_edges(curr)

            while len(ins) == 1 or (len(ins) == 2 and (ins[0][::-1] in H.edges() or ins[1][::-1] in H.edges())):
                prev = ins[0][0]
                if len(ins) == 2 and (curr, prev) in H.edges():
                    color_map[prev] = c
                    prev = ins[1][0]
                elif len(ins) == 2:
                    color_map[ins[1][0]] = c


                if color_map[prev] == -1:
                    color_map[prev] = c
                    curr = prev
                    ins = H.in_edges(curr)
                else: 
                    break




    color_max = max(color_map.values())
    values = [color_max - color_map.get(node, 1) for node in H.nodes()]

    return values, color_max

        
def remove_spur(g, threshold=3):
    '''移除g突出的边和点
    threshold: 突出边的节点数目
    '''
    from functools import reduce
    for n in [x for x in g.nodes() if g.out_degree(x) >= 2]:
        paths = []
        for p in g.successors(n):
            path = [n, p]
            while len(path) < threshold and g.in_degree(path[-1]) == 1 and g.out_degree(path[-1]) == 1:
                path.append(g.successors(path[-1])[0])

            paths.append(path)

        spurs = [path for path in paths if g.out_degree(path[-1]) == 0]
        if len(spurs) == len(paths):
            spurs.remove(reduce(lambda x,y: x if len(x) > len(y) else y, spurs, []))

        for path in spurs:
            [g.remove_edge(s, e) for s, e in zip(path[:-1], path[1:])]
            [g.remove_node(n) for n in path[1:]]


    for n in [x for x in g.nodes() if g.in_degree(x) >= 2]:
        paths = []
        for p in g.predecessors(n):
            path = [n, p]
            while len(path) < threshold and g.in_degree(path[-1]) == 1 and g.out_degree(path[-1]) == 1:
                path.append(g.predecessors(path[-1])[0])

            paths.append(path)

        spurs = [path for path in paths if g.in_degree(path[-1]) == 0]
        if len(spurs) == len(paths):
            spurs.remove(reduce(lambda x,y: x if len(x) > len(y) else y, spurs, []))

        for path in spurs:
            [g.remove_edge(s, e) for s, e in zip(path[1:], path[:-1])]
            [g.remove_node(n) for n in path[1:]]
        
    return g



def remove_bubble(g, threshold=10):
    '''去除小的bubble
    threshold: bubble的最长路径
    '''
    def reverse(path):
        return [p[:-1]+('E' if p[-1]=='B' else 'B') for p in path][::-1]

    start_nodes = set([x for x in g.nodes() if g.out_degree(x) == 2])   # TODO 可改成多个

    reverse_nodes = set()
    for n in start_nodes:
        if n in reverse_nodes: continue

        paths = []
        for p in g.successors(n):
            path = [n, p]
            while len(path) < threshold and g.in_degree(path[-1]) == 1 and g.out_degree(path[-1]) == 1:
                path.append(g.successors(path[-1])[0])

            
            paths.append(path)

        is_bubble = all([len(path) < threshold for path in paths]) and all([paths[0][-1] == path[-1] for path in paths[1:]])
        if is_bubble:
            for path in paths[1:]:
                [g.remove_edge(s, e) for s,e in zip(path[:-1], path[1:])]
                [g.remove_node(n) for n in path[1:-1]]

                vpath = reverse(path)
                print("path:", path)
                print("vpath:", vpath)
                [g.remove_edge(s, e) for s,e in zip(vpath[:-1], vpath[1:])]
                [g.remove_node(n) for n in vpath[1:-1]]
                reverse_nodes.add(vpath[0])

    return g



def remove_loop(g, flank=1000):
    '''
    将string graph的loop解开，增加新边和节点解决loop的重复区
        l_a         r_a
          \         /
           l ----- r
          /         \
        l_b         r_b
    '''
    def look_cross(curr, prev):
        steps = 0
        while steps < flank and g.in_degree(curr) == 1 and g.out_degree(curr) == 1:
            (steps, curr, prev) = (steps+1, g.successors(curr)[0], curr)
        print("step:", steps)
        return curr, prev


    print( [n for n in g.nodes() if g.out_degree(n) == 2])
    print( [n for n in g.nodes() if g.in_degree(n) == 2])
    # 阶段
    for r in [n for n in g.nodes() if g.out_degree(n) == 2]:
        
        (isloop, path) = (False, None)
        
        r_a, r_b = g.successors(r)
        
        l, l_a = look_cross(r_a, r)
        print("in left:", l, g.in_degree(l), g.out_degree(l))
        if g.in_degree(l) == 2 and g.out_degree(l) == 1:
            (r1, r1_prev) = look_cross(g.successors(l)[0], l)
            print("de:", g.in_degree(r1), g.out_degree(r1))
            print(r1, r, r1_prev)
            (isloop, path) = (r1 == r, (l_a, l, r, r_b))

        if not isloop:
            l, l_a = look_cross(r_b, r)
            if g.in_degree(l) == 2 and g.out_degree(l) == 1:
                (r1, r1_prev) = look_cross(g.successors(l)[0], l)
                (isloop, path) = (r1 == r, (l_a, l, r, r_a))

        if isloop:
            print("loop")
            attr = g.edge[path[0]][path[1]]
            print(attr)
            g.add_edge(path[0], path[1]+'X', attr)
            g.remove_edge(path[0], path[1])
            
            curr = path[1]
            while g.out_degree(curr) == 1:
                next = g.successors(curr)[0]
                attr = g.edge[curr][next]
                #g.remove_edge(curr, next)
                g.add_edge(curr+"X", next+"X", attr)
                curr = next

            assert g.out_degree(curr) == 2
            
            attr = g.edge[path[2]][path[3]]
            g.add_edge(path[2]+"X", path[3], attr)
            g.remove_edge(path[2],path[3])

    return g



def show_string_graph(g, loc, values, color_max):
    plt.figure(0)
    nx.draw_networkx(G, loc, with_labels=False, node_color=values,cmap = 'hsv',vmin = 0,vmax = color_max, node_size=8,linewidths=0.1)
    plt.show()
    


#def test_overlap():
#    import matplotlib.pyplot as plt
#    sg = StringGraph()
#    sg.add_overlap(0, 20, 5, 20, 1, 20, 0, 15)
#    sg.add_overlap(0, 20, 5, 20, 3, 20, 0, 15)
#    nx.draw(sg.graph)
#    plt.show()

if __name__ == "__main__":
    test_overlap()
