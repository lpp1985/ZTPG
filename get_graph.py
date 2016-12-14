#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2016/12/13
"""
from lpp import *
from Dependency import *
def GenerateOverlapGraph(FILE):
    
    Overlap_Graph = Contig_Graph()
    
    for line in FILE:
        data = []
        line_l = line.strip().split()
       
        Overlap_Graph.add_bi_path(line_l)  
    return Overlap_Graph
Overlap_Graph = GenerateOverlapGraph ( open(sys.argv[1]) )
print(Overlap_Graph.successors(sys.argv[2]))
print( len(  Overlap_Graph.successors(sys.argv[2])  )  )
print(Overlap_Graph.predecessors(sys.argv[2]))
print( len(  Overlap_Graph.predecessors(sys.argv[2])  )  )