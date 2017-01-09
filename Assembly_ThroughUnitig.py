#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/8/8


from lpp import *
import shutil,copy
from configure import *
from time import time
from hashlib import md5
from Dependency import *
import subprocess
from termcolor import colored
import shlex,os

from  optparse import OptionParser
from Circula import *

if __name__=='__main__':
	usage = '''usage: python2.7 %prog [options]
transfer trim overlap relationship'''
	parser = OptionParser(usage =usage )

	parser.add_option("-i", "--INPUT", action="store",
		              dest="inp", 
		              help="Input overlap")
	parser.add_option("-r", "--READS", action="store",
		                  dest="reads", 
		                  help="all Raw Reads")	


	parser.add_option("-o", "--out", action="store",
		              dest="output",
		              help="The output name you want!!") 

	parser.add_option("-u", "--uni", action="store",
		              dest="unitig",
		              help="Raw unitig sequence in fasta !!")


	(options, args) = parser.parse_args()
	inp = options.inp
	output = options.output
	if output.endswith(".detail"):
		output = re.sub("\.detail$","",output)
	unitig = options.unitig
	reads = options.reads
	all_reads = {}
	unitig_seq = Ddict()
	for t,s in fasta_check( open(reads,'rU')):
		name = t[1:].strip().split()[0]
		s = re.sub("\s+","",s)
		all_reads[name+'+']= s
		s1 = complement(s)
		all_reads[name+'-']= s1
	for t,s  in fasta_check( open(unitig,'rU')  ):
		name = t[1:].strip()
		start,end = name.split("__")
		unitig_seq[start][end]= re.sub("\s+","",s)
	END = open(output+".fasta",'w')
	STATUS = open(output+".status",'w')
	for line in open( options.inp):
		line_l = line.strip().split("\t")
		name = line_l[0]
		status = line_l[-1]
		need_list = line_l[1].split("; ")
		out_seq = all_reads[ need_list[0]  ]
		for i in xrange(0,len(need_list)-1):

			out_seq+= unitig_seq[ need_list[i] ][ need_list[i+1] ]
		END.write('>'+name+'\t'+status+'\n')
		END.write( out_seq +'\n')
		STATUS.write(name+'\t%s'%(len(out_seq))+'\t'+status+'\n')
	