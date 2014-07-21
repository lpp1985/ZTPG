#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/5



from optparse import OptionParser
import subprocess,shlex
from Dependency import *
import copy
def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option("-u","--UNI",action= "store",
                      dest = "uni",
                      help="Unitig Path contained best.edges file"
                      )
    
    parser.add_option("-u","--READ",action= "store",
                      dest = "read",
                      help=" best reads in Fasta format"
                      )
    
    parser.add_option("-o","--OUTPUT",action= "store",
                      dest = "output",
                      help="Output File"
                      )	
    parser.add_option("-s","--SEED",action= "store",
                      dest = "seed",
                      help="Seeds fasta file"
                      )		    

    (options, args) = parser.parse_args()
    return options,args





if __name__=='__main__':
    #获得参数
    options,args = get_para()
    overlapStore = options.overlap
    RAW = open( options.reference,'rU' )
    #载入参考图
    reference_Graph  = Get_Reference_Graph( RAW   ) 


    #载入overlap图
    BESTEDGE = open( options.uni+'best.edges','rU')
    overlap_Graph,all_nodes = Get_Overlap_Graph(BESTEDGE)

    Corrected_overlap_Graph = copy.copy(overlap_Graph)
    #根据reference graph修剪overlap graph
    for  reads in overlap_Graph.nodes():
        if reads not in  reference_Graph.nodes():
            continue
        succ = overlap_Graph.unique_succ(reads)
        candidate_3_reference = reference_Graph.successors(reads)[0]        
        if succ:
            if len(succ)==1:
                continue
            if succ=="Multi":
                if candidate_3_reference in overlap_Graph.successors(reads):
                    for candidate_3_overlap in overlap_Graph.successors(reads):
                        if candidate_3_overlap != candidate_3_reference:
                            Corrected_overlap_Graph.remove_bi_edge(  reads,candidate_3_overlap     )    
        else:
            data = subprocess.check_output( shlex.split( cele_path+'/overlap_check.py  -g %s -s %s -q %s    ' %(  overlapStore, reads,candidate_3_reference  )      )    )
            if data:

                Corrected_overlap_Graph.add_bi_edge(reads_3,candidate_3_reference)             



    DETAIL = open(options.output+'.detail', 'w')
    Contig_relation,plasmid_contig ,G_Output = Get_Contig(Corrected_overlap_Graph,DETAIL,'round1_')

    END = open(options.output+'.graph','w' )
    
    for key in G_Output.edges():
        END.write('\t'.join(key)+'\n')

    ##生成网页

    Draw_Web(options.output+'.graph.html', G_Output)
    ##生成Contig之间的关系
    RELA = open( options.output+'.rela' ,'w')
    for name,components in Contig_relation.items():
        RELA.write(name+'\t'+components[0]+'\t'+components[-1]+'\n')
        
    
    #guess_commandline = cele_path+"""/Find_Potential_Cycle.py  -p %(out)s.graph -s %(out)s.fasta -o %(out)s.optimize"""%(
        #{
            #"out":options.output
        #}
    #)

    #err = subprocess.Popen(  shlex.split( guess_commandline ),stderr=subprocess.PIPE  ).communicate()    