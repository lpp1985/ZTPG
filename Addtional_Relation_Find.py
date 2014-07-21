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

    Draw_Web("%s.html"%(options.output), G_Contig)
    total_cycle = Find_Cycle(G_Contig)
    DETAIL = open( options.output+".detail",'w')
    i=0
    for each_cycle in total_cycle:
        i+=1
        DETAIL.write("Addtional_Optimize%s\t%s\tPlasmid\n"%(   i,'; '.join(each_cycle)   )    )
    assembly_command = cele_path+"/Assembly_by_Nucmer.py  -i %s  -u %s  -o cache.fasta  "%(DETAIL.name,options.fasta)

    os.system(assembly_command)
    ENDSEQ = open(options.output+".fasta",'w')
    ENDSEQ.write(open('cache.fasta' ,'rU').read() )
    os.remove("cache.fasta")    