#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2014/7/18
"""

from Dependency import *

Overlap_Graph, all_nodes= Get_Overlap_Graph(open(sys.argv[1],'rU'))
Contig_relation, plasmid_contig,G_Output = Get_Contig(Overlap_Graph,open("detail",'w'),"lpp")
Draw_Web("./123.html",G_Output)
all_cycle = Find_Cycle(G_Output)
for cycle in all_cycle:
	print(cycle)
	
print(G_Output.nodes())
