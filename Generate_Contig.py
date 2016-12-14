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
    parser.add_option("-c", "--Cir", action="store_true",
                      dest="cir",
                      default=False,
            
                      help="The output name you want!!")   
    parser.add_option("-r", "--Alle", action="store_true",
                      dest="alle",
                      default=False,

                      help="The output name you want!!")       
    
    (options, args) = parser.parse_args()
    edge = options.edge
    alle = options.alle
    cir = options.cir
    if cir:
        alle= True
    output = os.path.abspath(options.output)
    Overlap_Graph = GenerateOverlapGraph( open(edge,'rU'))
    for line in open(options.node):
        
        Overlap_Graph.add_node(line.strip())
    
    
    
    DETAIL = open(options.output+'.detail', 'w')
    if cir:
        Overlap_Graph = Orphan_Removal(Overlap_Graph)
        Overlap_Graph,removed_node_hash = Alle_Removal(Overlap_Graph)
    Contig_relation,plasmid_contig ,G_Output,Contig_path = Get_Contig(Overlap_Graph,DETAIL,output.split('/')[-1])

    END = open(options.output+'.graph','w' )    
    Draw_Web(options.output+'.graph.html', G_Output)
    RELA = open( options.output+'.rela' ,'w')
    PLASMID = open( options.output+'.Plasmid' ,'w')
    for key,path in plasmid_contig.items():
        PLASMID.write( key+'\t'+'; '.join(path)+'\tPlasmid\n' )
        
    for name,components in Contig_relation.items():
        RELA.write(name+'\t'+components[0]+'\t'+components[-1]+'\n')    
        
    #去等位基因
   
    if alle:
        NewG_Output,removed_node_hash = Alle_Removal(G_Output)
        removed_path = []
        
        for each_removedcontig in removed_node_hash:
            
            removed_path.extend(  Contig_path[ each_removedcontig[:-1]+'+'  ]  )
        for node in removed_path:
            Overlap_Graph.remove_bi_node(node)
            
        DETAIL = open(options.output+'.Alle.detail', 'w')
        Assembled_Contig_no = 1
        Contig_relation,plasmid_contig ,G_Output,Contig_path = Get_Contig(Overlap_Graph,DETAIL,output.split('/')[-1])
        
        END = open(options.output+'.Alle.graph','w' )    
        Draw_Web(options.output+'.Alle.graph.html', G_Output)
        RELA = open( options.output+'.Alle.rela' ,'w')
        PLASMID = open( options.output+'.Alle.Plasmid' ,'w') 
        EDGE = open( options.output+'.Alle.edge' ,'w')
        for key,path in plasmid_contig.items():
            PLASMID.write( key+'\t'+'; '.join(path)+'\tPlasmid\n' )        
        for start,end in G_Output.edges():
            EDGE.write(  start+'\t'+end+'\n' )
        
        if cir:
            total_cycle = Find_Cycle(G_Output)
            name = output.split('/')[-1]+"_CirCular"
            i=0
    
            for each_cycle in total_cycle:
                i+=1 
                path = []
                for each_c in each_cycle:
                    if each_c[-1]=="+":
                        path.extend(  Contig_path[each_c]  )
                    else:
                        path.extend(  Reverse_Path(Contig_path[each_c[:-1]+'+'])  )
                PLASMID.write(name+str(i)+'\t'+'; '.join(path  )  +"\tPlasmid\n"  )
           
        