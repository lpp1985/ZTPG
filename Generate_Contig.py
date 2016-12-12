#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/19

from Dependency import *
from  optparse import OptionParser
def GenerateOverlapGraph(FILE):
    
    Overlap_Graph = Contig_Graph()
    
    for line in FILE:
        data = []
        line_l = line.strip().split()
       
        Overlap_Graph.add_bi_path(line_l)  
    return Overlap_Graph
        
all_nodes = {}
if __name__=='__main__':
    usage = '''usage: python2.7 %prog [options]
transfer trim overlap relationship'''
    parser = OptionParser(usage =usage )

    parser.add_option("-e", "--Edge", action="store",
                      dest="edge", 
                      help="edge Info") 
    parser.add_option("-n", "--Node", action="store",
                      dest="node", 
                      help="edge Info")     


    parser.add_option("-o", "--out", action="store",
                      dest="output",
                      help="The output name you want!!") 
    (options, args) = parser.parse_args()
    edge = options.edge
    output = os.path.abspath(options.output)
    Overlap_Graph = GenerateOverlapGraph( open(edge,'rU'))
    for line in open(options.node):
        
        Overlap_Graph.add_node(line.strip())
    
    
    
    DETAIL = open(options.output+'.detail', 'w')
    Contig_relation,plasmid_contig ,G_Output = Get_Contig(Overlap_Graph,DETAIL,'round1_')

    END = open(options.output+'.graph','w' )    
    Draw_Web(options.output+'.graph.html', G_Output)
    RELA = open( options.output+'.rela' ,'w')
    for name,components in Contig_relation.items():
        RELA.write(name+'\t'+components[0]+'\t'+components[-1]+'\n')    