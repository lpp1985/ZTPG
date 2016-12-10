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
        line_l = line.split()
        tag = "+"
        if line_l[8]=='-':
            tag = "-"
        data.append( str(int(line_l[0]))+'+' )
        data.append( str(int(line_l[1]))+tag )
        print(data)
        Overlap_Graph.add_bi_path(data)  
    return Overlap_Graph
        
all_nodes = {}
if __name__=='__main__':
    usage = '''usage: python2.7 %prog [options]
transfer trim overlap relationship'''
    parser = OptionParser(usage =usage )

    parser.add_option("-i", "--INPUT", action="store",
                      dest="inp", 
                      help="Input overlap") 


    parser.add_option("-o", "--out", action="store",
                      dest="output",
                      help="The output name you want!!") 
    (options, args) = parser.parse_args()
    inp = options.inp
    output = os.path.abspath(options.output)
    Overlap_Graph = GenerateOverlapGraph( open(inp,'rU'))
   
    
    
    
    DETAIL = open(options.output+'.detail', 'w')
    Contig_relation,plasmid_contig ,G_Output = Get_Contig(Overlap_Graph,DETAIL,'round1_')

    END = open(options.output+'.graph','w' )    
    Draw_Web(options.output+'.graph.html', G_Output)
    RELA = open( options.output+'.rela' ,'w')
    for name,components in Contig_relation.items():
        RELA.write(name+'\t'+components[0]+'\t'+components[-1]+'\n')    