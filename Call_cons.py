#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/6/14


from lpp import *
from optparse import OptionParser
from  termcolor import colored
from configure import nucmer,cele_path

def get_para(   ):
	#获得运行参数
	usage = '''
	%prog [ options ]
	'''
	parser = OptionParser( usage = usage  )


	parser.add_option("-c", "--Contig", action="store",
		              dest="contig",
		              help="Contig Sequence")
	parser.add_option("-a","--ALL",action= "store",
		              dest = "allreads",
		              help=" Fasta file record all reads "
		              )		
	parser.add_option("-o","--Output",action= "store",
		                  dest = "output",
		                  help=" Consensus sequence "
		                  )		
	(options, args) = parser.parse_args()
	return options,args


if __name__=='__main__':
	options,args = get_para()
	contig = options.contig
	allreads = options.allreads
	output = options.output
	seq_hash = {}
	seq_contig = {}
	
	for t,s in fasta_check(open(allreads,'rU')):
		seq_hash[t[1:-1]] = re.sub('\s+','',s)
		
	for t,s in fasta_check(open(contig,'rU')):
		seq_contig[t[1:-1].split()[0]] = re.sub('\s+','',s)	
		
	

	NUCMER = os.popen(nucmer +"""  --maxmatch %s %s  -p cons 2>/dev/null 1>&2 && show-coords  cons.delta  -orlcdT| grep "\[CONTA" """%(
	    contig,allreads
	)
	                  )

	has = {}
	for line in NUCMER:
		line_l = line.split("\t")
		frame = line_l[12]
		seq_name = line_l[13]
		if seq_name not in has:
			if has:
				os.system(cele_path+"/pbutgcns -j 64 %s >> %s"%(END.name,output))
			has[seq_name] = ""
			END = open(seq_name+'.lay','w')
			END.write("%s %s\n"%(seq_name,seq_contig[seq_name]))
		ref_start, ref_stop = str( int(line_l[0])-1 ), line_l[1]          
		if frame=="1":
			query_start ,query_stop = str( int(line_l[2])-1 ), line_l[3] 
			que_seq = seq_hash[line_l[-2]]
		else:
			query_start ,query_stop = str( int(line_l[3])-1 ), line_l[2] 
			que_seq = complement(seq_hash[line_l[-2]])
			
		que_need_seq = que_seq[int(query_start) :    int(query_stop) ]
		END.write("%s %s %s %s\n"%(line_l[-2],ref_start,ref_stop,que_seq  ))
	os.system(cele_path+"/pbutgcns -j 64 %s >> %s"%(END.name,output))
