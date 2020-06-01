# 概述
这里实现论文所描述的算法。

    A Fast and Accurate Algorithm for Single Individual Haplotyping Based on a Two-Locus Linkage Graph

算法大致步骤：
1. 构建Two-Locus Linkage Graph
2. 标注节点值（Haplotype值）并确定error-tolerant子图。
3. 以子图为节点构建新图
4. 纠正节点（子图）内flagment不一致的值
5. 如果步骤4没有改动或者只有一个节点，进入步骤6，否则进入步骤2
6. 每个节点为block，按照block输出节点标注的值。

本代码与论文的不同点：
1. Haplotype值，代码采用{-1,1,0}，论文采用{0,1,-}。
2. 论文步骤是先4后3。
