#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/19


from lpp import *
import os

from optparse import OptionParser

def get_para(   ):
	#获得运行参数
	usage = '''
	%prog [ options ]
	'''
	parser = OptionParser( usage = usage  )


	parser.add_option("-q", "--Query", action="store",
	                  dest="query",
	                  help="Raw Reads in Fasta Format!!!")





	parser.add_option("-i","--Identity",action= "store",
	                  dest = "identity",
	                  type="float",
	                  default=0.95,
	                  help="Identity!"
	                  )		

	parser.add_option("-o","--OUT",action= "store",
	                  dest = "output",
	                  help="output file"
	                  )		
	parser.add_option("-l","--LENGTH",action= "store",
	                  dest = "length",
	                  type="int",
	                  default=1000,
	                  help="Overlap Length"
	                  )	
	parser.add_option("-a","--Assembly",
	                  dest="assembly",
	                  action = "store_true",
	                  default = False,
	                  help="Assembly?"
	                  )			
	parser.add_option("-c","--Circular",
	                  action = "store_true",
	                  dest="circular",
	                  default = False,
	                  help="Guess Circluar"
	                  )		

	(options, args) = parser.parse_args()
	return options,args
if __name__=="__main__":
	options,args = get_para()

	query = options.query
	identity = options.identity
	output = options.output
	name =  os.path.splitext(query)[0]
	overlap_length = options.length
	assembly = options.assembly
	circluar = options.circular


	all_name = name+".all.fasta"
	format_name = name+".format.fasta"
	format_Reads_command = '''DB_Reads -i %(reads)s  -f %(name)s  -o %(out)s -r %(all)s'''%( 
	    {
	        "reads":query,
	        "out":format_name,
	        "all":all_name,
	        "name":"Query"

	    }
	)
	os.system(format_Reads_command)

	buildDB_Command = '''fasta2DB Reads %(reads)s '''%( 
	    {
	        "reads":format_name
	    }    
	)	
	os.system(buildDB_Command)

	splitDB_Command = '''DBsplit Reads'''    
	os.system(splitDB_Command)

	SeqAlign_Command = '''HPC.daligner -v -B40 -T32 -t16 -e%s -l1000 -s1000 Reads | csh -v '''%(identity)

	os.system( SeqAlign_Command )
	MergeAlign_Command = '''LAmerge  Alignment Reads*.las && rm Reads*.las'''
	os.system(MergeAlign_Command)
	SortAlign_Command = '''LAsort  Alignment && mv Alignment.S.las Alignment.las''' 
	os.system(SortAlign_Command)
	LA4Falcon_Command = '''LA4Falcon -mog Reads  Alignment >Alignment.m4''' 
	os.system(LA4Falcon_Command)

	os.system("rm Reads.db ")
	os.system("rm .Reads.*")

	Filter_Command = "DAFilter -i Alignment.m4 -o FilterAlignment.m4"

	os.system(Filter_Command)

	Transitive_Command = "Transitive_Remove -i FilterAlignment.m4  -l %s -g OVL -o Graph.detail"%(overlap_length)
	os.system(Transitive_Command)
	if assembly:
		Unitig_Generate = "Generate_Unitig -f %s  -i Graph.detail -o Unitig_element.fasta"%( all_name  )
		os.system(  Unitig_Generate )
		Contig_Generate = "Generate_Contig.py  -e OVL.edges  -n OVL.nodes  -o ./%s.contig"%(output)
		os.system(  Contig_Generate )
		Assembly_Generate = " Assembly_ThroughUnitig.py  -i ./%s.contig.detail  -r %s  -o ./%s.contig -u Unitig_element.fasta  " %( output,all_name, output )
		
		os.system(Assembly_Generate)
 
	if circluar:
		Circle_Generate = "Find_Circle_Denovo.py  -i %s -o %s.Cir -g OVL.edges "%( all_name, output)
		print( Circle_Generate )
		os.system(Circle_Generate)
		




