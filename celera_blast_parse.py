#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/15


from lpp import *

RAW = open( sys.argv[1],'rU'  )
all_data = {}
has = {}
has_start = {}
has_end = {}
RAW.next()
for line in RAW:
	line_l = line.split('\t')
	length = int( line_l[3]  )
	name = line_l[2]
	start,end = sorted( [int( line_l[13 ])  ,int( line_l[14] ) ])

	if name in has:
		continue
	if (end-start )>= length-1000:
		all_data[  line ] = ''
		has[ name  ] = ''
	elif start <=500 and name not in has_start:
		all_data[line] = ''
		has_start[name ] = ''
	elif length-end <=500 and name not in has_end:
		all_data[line] = ''

		has_end [ name ] = ''
	if name in has_end and name in has_start:
		has[name] = ''
		
END = open( sys.argv[2],'w' )
for line in sorted(   all_data, key = lambda x: int( x.split('\t')[15]   ), cmp = lambda x,y:cmp( x   ,y     )):
	END.write( line )