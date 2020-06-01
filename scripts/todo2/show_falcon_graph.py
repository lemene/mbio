'''显示falcon生成的string graph
show.py sg_edges_list strand loop
strand：显示单双链
loop：是否显示解环

程序需要：sg_edges_list_X_X.png.loc文件，由forceatlas2生成
根据
'''

import matplotlib.pyplot as plt
import networkx as nx
import pickle

import sys
sys.path.append(r"e:\work\mbio")

import mbio.string_graph as sg

# (单链, 双链) X (解环, 不解环)

g = sg.load_falcon_graph(sys.argv[1])
g = list(nx.weakly_connected_component_subgraphs(g))[1]
g = sg.remove_bubble(g)
g = sg.remove_spur(g)
g = sg.remove_bubble(g)

single_strand = False if len(sys.argv) <= 2 else int(sys.argv[2]) > 0
loop_resolution = False if len(sys.argv) <= 3 else int(sys.argv[3]) > 0

print(single_strand, loop_resolution)

if loop_resolution:
    g = sg.remove_loop(g)

    if single_strand:
        g = sg.connect_strand(g)
        (values, color_max, loc) = pickle.load(open(sys.argv[1]+"_S_L.png.loc", "rb"))
    else:
        (values, color_max, loc) = pickle.load(open(sys.argv[1]+"_L.png.loc", "rb"))

else:
    if single_strand:
        g = sg.connect_strand(g)
        (values, color_max, loc) = pickle.load(open(sys.argv[1]+"_S.png.loc", "rb"))
    else:
        (values, color_max, loc) = pickle.load(open(sys.argv[1]+".png.loc", "rb"))



for x in [x for x in loc if x[-1] == 'X']: 
    print(x, x[0:-3]+":X:"+x[-2:-1])
    loc[x[0:-3]+":X:"+x[-2:-1]] = loc[x]

values, color_max = sg.set_colors(g) # 重新上颜色，因为颜色和节点位置可能不匹配
print(len(g.nodes()))

plt.figure(0)
nx.draw_networkx(g, loc, with_labels=False, node_color=values,cmap = 'hsv',vmin = 0,vmax = color_max, node_size=8,linewidths=0.1)
plt.show()


