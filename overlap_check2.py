#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/9

from optparse import OptionParser
from lpp import *
import subprocess,shlex
from Dependency import *
def get_para(   ):
	#获得运行参数
	usage = '''
	%prog [ options ]
	'''
	parser = OptionParser( usage = usage  )
	
	
	parser.add_option("-g", "--OVL", action="store",
		              dest="ovl",
		              help="overlapStore")
	
	parser.add_option("-q","--QUERY",action= "store",
		              dest = "query",
		              help="Query Reads ID!"
		              )
	parser.add_option("-s","--SUB",action= "store",
		                  dest = "subject",
		                  help="Subject Reads ID"
		                  )	
	(options, args) = parser.parse_args()
	return options,args
options,args = get_para()
overlstore = options.ovl
queryID = options.query
subjectID = options.subject

overlap_PATH =celera_assembler+'/overlapStore'

#运行overlapStore，检查两个reads是否具有overlap的结果

check_GRAPH = Contig_Graph()

check_GRAPH.add_bi_edge(queryID,subjectID)
for queryID,subjectID in check_GRAPH.edges():

	if queryID.endswith('+'):
		direction = '3'
		break
	elif subjectID.endswith('+'):
		direction ='5'
		break
#检查是否是3‘或者5’端overlap

if direction =='3':

	command =  overlap_PATH+''' -d %(overlap)s     -b %(query)s -e %(query)s -d3 | grep -P "\s+%(subject)s\s+"'''%( 
		    {
		        'overlap':overlstore,'query':queryID[:-1],'subject':subjectID[:-1] }  
		)
	
	
	detailout = os.popen(
		command 
		)
	#all_detail_block = detailout.split('\n')
	for line in detailout:

		detail_block = line.strip().split()
		if not detail_block:
			continue
		
		if subjectID[:-1]== detail_block[1]:
	
	
			arrange = detail_block[2]
			if arrange=='N':
				read_dir = '+'
			else:
				read_dir='-'
			if read_dir==subjectID[-1]:
				print("Yes")
else:
	command =  overlap_PATH+''' -d %(overlap)s     -b %(subject)s -e %(subject)s -d5 | grep -P "\s+%(query)s\s+"'''%( 
	    {
	        'overlap':overlstore,'query':queryID[:-1],'subject':subjectID[:-1] 
	    }  
	)
		


	detailout = os.popen(
        command 
        )

	for line in detailout:
		detail_block = line.strip().split()
		if not detail_block:
			continue
		if queryID[:-1]== detail_block[1]:
	
	
			arrange = detail_block[2]
			if arrange=='N':
				read_dir = '+'
			else:
				read_dir='-'
			if read_dir==queryID[-1]:
				print("Yes")	
