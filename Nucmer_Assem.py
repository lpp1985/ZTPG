#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2014/4/9
from Dependency import *

def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option("-i", "--Input", action="store",
                      dest="fasta",
                      help="Contig Sequence in Fasta Format")

    parser.add_option("-o","--Ouptut",action= "store",
                      dest = "output",
                      help=" Result Suffix "
                      )


    (options, args) = parser.parse_args()
    return options,args


if __name__=='__main__':
    options,args = get_para()
    raw_file = options.fasta
    output_category = Mummer_parse( raw_file  )

    G_Contig= Relation_parse( raw_file, output_category, options.output )
    
    #total_cycle = Find_Cycle(G_Contig)
    DETAIL = open( options.output+".detail",'w')
    i=0
    New_Graph = Contig_Graph()
    Contig_relation,plasmid_contig ,G_Output = Get_Contig(G_Contig,DETAIL,'round1_')
    Draw_Web("%s.html"%(options.output), G_Output)
    
