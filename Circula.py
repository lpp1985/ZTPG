#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2014/4/2
import os,tempfile,sys
sys.path.append(os.path.split(__file__)[0]+'/../Lib/')
from lpp import *
from optparse import OptionParser

import subprocess
#对拼接结果进行环化
def Circulation(sequence):
	sequence = re.sub( "\s+","",sequence )
	RAW = open(tempfile.mktemp() ,'w' )
	RAW.write(">RAW\n%s\n"%(  sequence ) )
	HEAD = open(tempfile.mktemp() ,'w' )
	HEAD.write( ">HEAD\n%s\n"%( sequence[  : len(sequence)/2 ]   )  )
	command_line = """ nucmer --maxmatch %s %s 1>/dev/null 2>/dev/null && show-coords -coHT  out.delta | grep "\[END\]"   """%( RAW.name,HEAD.name  ) 
	
	stdout = os.popen( command_line  ).read()
	try:
		start_location = int(stdout.split()[0])-1
		end = sequence[:start_location]
		end = re.sub( "(\w{60})" ,"\\1\n", end )
	except:
		if Veri:
			raise Exception( "%s is Error!"%(t.split())  )
		return sequence,"Linear"

	return end.upper(),"Circle"

if __name__=="__main__":
	usage = "python2.7 %prog [options]"
	parser = OptionParser(usage =usage )	
	parser.add_option("-i", "--Input", action="store",
		              dest="Input",
	
		              help="Input Fasta")
	parser.add_option("-o", "--Output", action="store",
		              dest="output",
	
		              help="OutputPath")
	parser.add_option("-v", "--Verification", 
	                  action="store_true",
	                  dest="verfi",
	                  help="Assembly Verification?")
	(options, args) = parser.parse_args()
	Input = options.Input
	Output = options.output	
	Veri = options.verfi
	RAW = fasta_check(open(Input,'rU'))
	END = open(Output,'w')
	STATS = open(Output+'.status','w')
	for t,s in RAW:
		
		s,status = Circulation(s)
		END.write(t.split()[0]+"  %s\n"%(status)+s+'\n')
		s1 = re.sub("\s+", "", s)
		STATS.write(t.split()[0][1:] +'\t%s\t%s\n'%(  status,len(s1)    )  )
		
