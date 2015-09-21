#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/9/1
"""
import networkx as nx
from Dependency import Contig_Graph
from lpp import *
graph = Contig_Graph()
RAW = open(sys.argv[1],'rU')
status = File_dict(open(sys.argv[2],'rU')).read(1,3)

for line in RAW:
    data = line.strip().split("\t")
    graph.add_bi_edge(data[0],data[1])
while True:
    start = raw_input("Start\n").strip()
    end = raw_input("End\n").strip()
    graph.add_bi_node(start)
    graph.add_bi_node(end)
    print("=============")
    for path in nx.algorithms.all_simple_paths(graph,start,end):
        for nodes in path:
            print(nodes+'\t'+status[nodes[:-1]])
        
    print("=============")
