#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/6/14


from lpp import *
from optparse import OptionParser
from  termcolor import colored
from configure import celera_assembler
import subprocess
def get_para(   ):
	#获得运行参数
	usage = '''
	%prog [ options ]
	'''
	parser = OptionParser( usage = usage  )


	parser.add_option("-b", "--BEST", action="store",
		              dest="best",
		              help="Location of best.edges file location")



	parser.add_option("-g","--GKP",action= "store",
		              dest = "gkp",
		              help=" GoalKeeper Directoty "
		              )	
	parser.add_option("-o","--OUT",action= "store",
		              dest = "output",
		              help=" Fasta file record all reads appeared in best.edges file "
		              )	
	parser.add_option("-a","--ALL",action= "store",
		              dest = "allreads",
		              help=" Fasta file record all reads "
		              )		
	(options, args) = parser.parse_args()
	return options,args


if __name__=='__main__':
	options,args = get_para()
	best = options.best

	gkp = options.gkp
	output = options.output
	all_read = options.allreads
	all_nodes = {}
	for line in open( best+'/best.edges','rU'):
		if '#' in line:
			continue
		data = []
		line_l = line[:-1].split('\t')
		all_nodes[ line_l[0]  ] = ''
		all_nodes[ line_l[2] ] = ''
		all_nodes[ line_l[4]  ] = ''
	print( colored("We Have %s Best reads!!"%(len(all_nodes)),"yellow") )
	
	commandline = celera_assembler+'/gatekeeper  -dumpfragments -withsequence %s'%( gkp )
	END = open(output,'w'  )
	ALL = open(all_read,'w')
	READS_DATA = os.popen( commandline  )
	data = re.split( "\n(?=fragmentIdent)" ,READS_DATA.read())
	for each_block in data:
		try:
			frag_id = re.search("\n*fragmentIdent\s+=\s+\d+\,(\d+)",each_block).group(1)
			
		except:
			
			print each_block
		sequence = re.search("fragmentSequence\s+\=\s+(\S+)",each_block).group(1)
		ALL.write('>%s\n'%(frag_id )+sequence +'\n')
		if frag_id in all_nodes:
			
			END.write( '>%s\n'%(frag_id )+sequence +'\n')