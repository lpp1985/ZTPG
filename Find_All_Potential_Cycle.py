#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2014/6/10
"""

from Dependency import *
#读取Contig_Graph
def get_para(   ):
	#获得运行参数
	usage = '''
	%prog [ options ]
	'''
	parser = OptionParser( usage = usage  )


	parser.add_option("-p", "--Graph", action="store",
		              dest="graph",
		              help="Overlap_graph")


	parser.add_option("-s","--SEQUENCE",action= "store",
		              dest = "sequence",
		              help=" Contig Sequence Zipper Out"
		              )

	parser.add_option("-o","--Ouptut",action= "store",
		              dest = "output",
		              help=" Result Suffix "
		              )


	(options, args) = parser.parse_args()
	return options,args


if __name__ == '__main__':
	options,args = get_para()
	GRAPH = open(options.graph,'rU')
	Seq_Graph = Contig_Graph()
	all_cycle = {}
	in_cycle = {}
	optimize_cycle = {}
	for line in GRAPH:
		line_l = line.strip().split("\t")
		if line_l[0] ==line_l[1]:
			continue
		Seq_Graph.add_bi_path(line.strip().split("\t"))
		
	DETAIL = open(options.output+'.detail','w' )
	
	i=0
	longest_path = ""
	for each_path in Find_Cycle(Seq_Graph):
		if len(longest_path)<len(each_path):
			longest_path = each_path
		path_string = '; '.join(each_path)
		
	
		i+=1
		DETAIL.write("Optimize%s"%(i)+'\t'+path_string+"\tPlasmid\n")
	DETAIL.write("Longest1"+"\t"+'; '.join(longest_path)+"\tPlasmid\n")
	#print(longest_path)
	assembly_command = cele_path+"/Assembly_by_Nucmer.py  -i %s  -u %s  -o cache.fasta  "%(DETAIL.name,options.sequence)
	
	os.system(assembly_command)
	
	ENDSEQ = open(options.output+'.fasta','w')
	for t,s in fasta_check(open(options.sequence,'rU')):
		name = t.strip()[1:].split("\t")[0]

		ENDSEQ.write(t+s)
	ENDSEQ.write(open('cache.fasta' ,'rU').read() )
	os.remove("cache.fasta")
	
