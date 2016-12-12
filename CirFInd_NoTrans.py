#!/usr/bin/env python
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
	parser.add_option("-g","--Graph",action= "store",
		              dest = "graph",
		              help=" Overlap Graph "
		              )	


	(options, args) = parser.parse_args()
	return options,args


if __name__=='__main__':
	options,args = get_para()
	raw_file = options.fasta
	G_Contig = Contig_Graph()
	for line in open(options.graph,'rU'):
		line_l  = line.strip().split("\t")
		G_Contig.add_bi_edge(line_l[0],line_l[1])
		

	Draw_Web("%s.html"%(options.output), G_Contig)
	total_cycle = Find_Cycle(G_Contig)
	DETAIL = open( options.output+".detail",'w')
	i=0
	New_Graph = Contig_Graph()
	for each_cycle in total_cycle:
		i+=1
		New_Graph.add_bi_cycle(each_cycle)
		DETAIL.write("Addtional_Optimize%s\t%s\tPlasmid\n"%(   i,'; '.join(each_cycle)   )    )
	Multi_Graph = Contig_Graph()
	doubt_node = {}
	for each_node in New_Graph.node:
		if len(New_Graph.successors(each_node))>=2 and len(New_Graph.predecessors(each_node))>=2:

			if each_node not in Multi_Graph.node:
				doubt_node[each_node] = ''
				Multi_Graph.add_bi_node(each_node)
	if len(doubt_node)==1:
		for each_doubt in doubt_node:
			new_node_name = "same_as_"+each_doubt
			New_Graph.add_bi_node(new_node_name)
			New_Graph.same(each_doubt, new_node_name)

	already_have = []
	for each_cycle in Find_Cycle(New_Graph):
		Multi_Graph = Contig_Graph()
		path = "  ".join(each_cycle)
		name = re.search("same_as_(\S+)",path)
		if name and name.group(1) in each_cycle:

			Multi_Graph.add_bi_cycle(each_cycle)
			all_node = Multi_Graph.node
			if all_node not in already_have:
				i+=1
				DETAIL.write("Addtional_Optimize%s\t%s\tPlasmid\n"%(   i,'; '.join(each_cycle).replace("same_as_","")   )    )
				already_have.append(all_node)
			else:
				continue

	assembly_command = cele_path+"/Assembly_by_daligner.py  -i %s  -u %s  -o %s  "%(DETAIL.name,options.fasta,options.output+".fasta")

	os.system(assembly_command)
	ENDSEQ = open(options.output+".fasta",'a')  

