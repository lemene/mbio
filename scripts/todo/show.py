import networkx as nx

import forceatlas2
import sys
import matplotlib.pyplot as plt 
import random
import cython

def show_graphml(fname):
    H = nx.read_graphml(fname)
    G = H.to_undirected()
    pos = { i : (random.random(), random.random()) for i in G.nodes()} 
    loc = forceatlas2.forceatlas2_networkx_layout(G, pos, niter=10)
    


    max_chr = 1
    for x in H.nodes():
        try:
            max_chr = max(max_chr,H.node[x.lstrip('B')]['chr'])
        except:
            pass

    chr_lengths = [0]*max_chr
    for x in H.nodes():
        try:
            chr_num = H.node[x.lstrip('B')]['chr']
            chr_lengths[chr_num-1] = max(chr_lengths[chr_num-1],H.node[x.lstrip('B')]['aln_end'])
        except:
            pass

    color_map = {}
    for x in H.nodes():
        try:
            chr_num = H.node[x.lstrip('B')]['chr']
            color_map[x] = sum(chr_lengths[0:chr_num-1]) + (chr_num-1)*600000 + H.node[x.lstrip('B')]['aln_end']
        
        except:
            color_map[x] = 5


    color_max = max(color_map.values())
    values = [color_max - color_map.get(node, 1) for node in G.nodes()]

    nx.draw_networkx(G, loc, with_labels=False, node_color=values,cmap = 'hsv',vmin = 0,vmax = color_max, node_size=8,linewidths=0.1) 

    plt.savefig("a.png")
    plt.show()


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

def show_graphml_branch(fname):
    H = nx.read_graphml(fname)
    G = H.to_undirected()
    

    values, color_max = set_colors(H)

    pos = { i : (random.random(), random.random()) for i in G.nodes()} 
    loc = forceatlas2.forceatlas2_networkx_layout(G, pos, niter=500)


    nx.draw_networkx(G, loc, with_labels=False, node_color=values,cmap = 'hsv',vmin = 0,vmax = color_max, node_size=8,linewidths=0.1) 

    plt.savefig("a.png")
    plt.show()

if __name__ == '__main__':
    show_graphml_branch(sys.argv[1])

    

#H = nx.read_graphml(sys.argv[1])
#G = H.to_undirected()
#pos = { i : (random.random(), random.random()) for i in G.nodes()} 

#nx.draw_networkx(G, l, with_labels=False,cmap = 'hsv',vmin = 0, node_size=8,linewidths=0.1) 
#plt.savefig("a.png")
#plt.show()

