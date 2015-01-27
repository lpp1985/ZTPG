#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2014/4/2
from lpp import *
import os,tempfile,sys
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
		start_location = int(stdout.split()[0])
		end = sequence[:start_location]
		end = re.sub( "(\w{60})" ,"\\1\n", end )
	except:
		print(command_line)
		return sequence

	return end.upper()

if __name__=="__main__":
	RAW = fasta_check(open(sys.argv[1],'rU'))
	END = open(sys.argv[2],'w')
	for t,s in RAW:
		
		s = Circulation(s)
		END.write(t+s+'\n')
	
		
