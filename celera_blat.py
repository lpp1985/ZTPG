#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/17


from lpp import *
from optparse import OptionParser
import subprocess,shlex
from Dependency import *
def get_para(   ):
        #获得运行参数
        usage = '''
	%prog [ options ]
	'''
        parser = OptionParser( usage = usage  )


        parser.add_option("-r", "--REF", action="store",
                          dest="ref",
                          help="Location of Reference sequence in fasta format!!!")


        parser.add_option("-b","--Best",action= "store",
                          dest = "best",
                          help="Reads which in best.edges "
                          )
        parser.add_option("-o","--Ouptut",action= "store",
                          dest = "output",
                          help="Reads which in best.edges "
                          )


        (options, args) = parser.parse_args()
        return options,args
if __name__=='__main__':

        options,args = get_para()
        referece = options.ref
        best_edges = options.best
        output = options.output
        
        data = subprocess.call(    shlex.split(  
                cele_path+'/Multi_blat.py  -d %(reference)s  -c 50 -o ./cache/blat_result  -i %(bestedges)s'%( 
                {'reference':referece,'bestedges':best_edges } 
                ) 
        ) 
                                                )

        RAW = open( './cache/blat_result','rU' )

        for line in RAW:
                if line.startswith( '-------------'  ):
                        break
        all_data = Ddict()
        for line in RAW:

                if not line :
                        continue
                if not re.match( '(^\d+\t)',line  ):
                        continue

                line_l = line.split('\t')
                all_data[  line_l[9]   ][ int( line_l[12] ) - int( line_l[11]  )  ] = line
        best_one = {}
        for key in all_data:


                key2 = sorted(  all_data[key].keys())[-1]

                if key2 <= int(all_data[key][key2].split()[10])*0.75 or int(all_data[key][key2].split()[10])- key2>4000:
                        continue
                best_one[ all_data[key][key2]  ] = ''

        best_one1 = sorted( best_one.keys(),key = lambda x: int( x.split('\t')[16] )   )
        best_one2 = sorted( best_one1,key = lambda x: int( x.split('\t')[15] )   )
        best_one3 = sorted( best_one2,key = lambda x: x.split('\t')[13]    )
        END = open( output,'w' )
        for key1 in best_one3:
                line_l = key1.split('\t')

                END.write( line_l[13]+'\t'+line_l[9]+line_l[8]+'\n' )
