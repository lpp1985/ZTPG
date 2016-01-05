#!/usr/bin/env python
#coding:utf-8
# Author:   >
# Purpose: 
# Created: 2014/4/23
import sys
from Dependency import Get_Overlap_Graph
from  termcolor import colored

DATA = open( sys.argv[1],'rU' )
edges=[]
G,all_nodes = Get_Overlap_Graph (DATA)
node = sys.argv[2]
print( colored( "Pressucor",'red') )
print( ';'.join(G.predecessors( node   ))    )

print( colored( "Succor" ,"blue" )  )
print( '; '.join( G.successors(  node  ) )  )
