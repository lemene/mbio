import networkx as nx

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



#def test_overlap():
#    import matplotlib.pyplot as plt
#    sg = StringGraph()
#    sg.add_overlap(0, 20, 5, 20, 1, 20, 0, 15)
#    sg.add_overlap(0, 20, 5, 20, 3, 20, 0, 15)
#    nx.draw(sg.graph)
#    plt.show()

if __name__ == "__main__":
    test_overlap()
