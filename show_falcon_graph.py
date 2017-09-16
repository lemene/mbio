import networkx as nx
import matplotlib.pyplot as plt
import forceatlas2
import random

#def show_graph(g):
#    #nx.draw(subgraph[1], with_labels=True)
#    pos = nx.circular_layout(g)
#    nx.draw_networkx(g, pos, with_labels=True)
#    plt.show()

def combine_strand(g):
    for n in g.nodes():
        if n[-1] == 'E' or n[-1] == 'B':
            g.add_edge(n[:-1]+'E', n[:-1]+'B')
            g.add_edge(n[:-1]+'B', n[:-1]+'E')

    return g


def load_falcon_graph(edges_list_file):
    graph = nx.DiGraph()

    with open(edges_list_file) as f:
        for line in f:
            e = line.strip().split()
            if e[7] == "G":
                graph.add_edge(e[0][6:], e[1][6:])

    return graph

def set_colors(H):
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

def remove_bubble(g, threshold=10):
    '''去除小的bubble'''
    start_nodes = set([x for x in g.nodes() if g.out_degree(x) == 2])   # TODO 可改成多个

    for n in start_nodes:

        paths = []
        for p in g.successor(n):
            path = [p]
            while len(path) < threshold and g.in_degree(path[-1]) == 1 and g.out_degree(path[-1]) == 1:
                path.append(g.successor(path[-1])[0])

            
            paths.append(path)

        is_bubble = all([len(path) < threshold for path in paths]) and all([paths[0][-1] == path[-1] for path in paths[1:]])
        if is_bubble:
            for path in paths:
                [g.remove_edge(s, e) for s,e in zip(path[:-1], path[1:])]
                [g.remove_node(n) for n in zip(path[1:-1])]

    return g
            

def show_graph(H):
    G = H.to_undirected()
    

    values, color_max = set_colors(H)

    pos = { i : (random.random(), random.random()) for i in G.nodes()} 
    loc = forceatlas2.forceatlas2_networkx_layout(G, pos, niter=500)


    nx.draw_networkx(G, loc, with_labels=False, node_color=values,cmap = 'hsv',vmin = 0,vmax = color_max, node_size=8,linewidths=0.1) 

    plt.savefig("a.png")
    plt.show



if __name__ == "__main__":
    import sys

    graph = load_falcon_graph(sys.argv[1])
    show_graph(graph)



