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

def Get_AllReads(file_name):
    max_length= 0
    all_data = {}
    DATA = fasta_check(open(file_name,'rU') )
    for t,s in DATA:
        s = re.sub("\s+",'',s)
        s_ = complement(s)
        if len(s)>max_length:
            max_length=len(s)
        name =t[1:].split()[0]
        all_data[name+'+']=s
        all_data[name+'-']=s_
        
    return all_data,max_length

def Single_Assembly(RAW,OUTPUT,all_raw_seq_hash):
    #store all sequence to a hash to prepare for output
    root_path = os.getcwd()
    STATUS = open( re.sub("[^\.]+$",'status',OUTPUT.name) ,'w')   
    STATUS.write("ID\tStatus\tLength\n")
    for line in RAW:
        line = line.strip()
        line_l = line.strip().split('\t')
        end_sequence = ''
        contig_list = line_l[1].split('; ')
        if len(contig_list)==1:
            OUTPUT.write(">%s\t%s\n%s\n"%( 
                line_l[0], line_l[-1], all_raw_seq_hash[line_l[1]  ]   
            )
                         )
            STATUS.write(
                line_l[0]+'\t'+line_l[-1].strip()+'\t%s\n'%(
                    len(
                        re.sub("\s+","",all_raw_seq_hash[line_l[1]  ])
                    )
                )
            )            
        else:
            i=0
            all_reads = {}
            out_path = os.path.dirname( os.path.abspath(OUTPUT.name) )
            assembly_path = out_path+'/assembly_new/'

            cache_path = assembly_path+line_l[0]+'/'
            check_path(  cache_path   )
            CACHE_READS = open(    cache_path+'reads.fasta','w'  )
            for each_data in contig_list:
                
                CACHE_READS.write('>reads/%s/0_%s\n%s\n'%(i,len( all_raw_seq_hash[  each_data  ] ) - 1,all_raw_seq_hash[  each_data  ] ) )
                all_reads[i] = all_raw_seq_hash[  each_data  ]
                i+=1
            print('''
            cd %(path)s
            fasta2DB %(out)s.db %(query)s &&
            DBsplit %(out)s&&
            daligner -e.95 -A %(out)s %(out)s&&
            LAmerge   %(prefix)s %(out)s*.las
            rm %(out)s*.las
            LAsort %(prefix)s.las
            LA4Falcon -mog %(out)s %(prefix)s.S.las&&cd %(back)s
                '''%(
                       {
                           "back": os.getcwd(),
                           "path":cache_path,
                           "query":CACHE_READS.name,
                           "out":cache_path+'/reads',
                           "prefix": cache_path+'/out'
                       }
                   )  
                   )
            nucmer_out = os.popen(
                '''
            cd %(path)s
            fasta2DB %(out)s.db %(query)s &&
            DBsplit %(out)s&&
            daligner -e.95 -A %(out)s %(out)s&&
            LAmerge   %(prefix)s %(out)s*.las
            rm %(out)s*.las
            LAsort %(prefix)s.las
            LA4Falcon -mog %(out)s %(prefix)s.S.las&&cd %(back)s
                '''%(
                       {
                           "back": os.getcwd(),
                           "path":cache_path,
                           "query":CACHE_READS.name,
                           "out":cache_path+'/reads',
                           "prefix": cache_path+'/out'
                       }
                   ) 
            )
            all_has = {}
            output_seq_hash = {}
            for data in nucmer_out:
                if data in all_has:
                    continue
                all_has[data] = ''
                data_l = data.strip().split()
                
                if data_l[-1]=="overlap":
                    print(data_l)
                    end_node = max( [ int(data_l[0]), int(data_l[1])  ]  )
                    if int(data_l[1]) - int(data_l[0]) ==1 and data_l[4] =="0" and data_l[8]=="0":
                        if int(data_l[8])  - int(data_l[7]) <100 and  int(data_l[9])<100:
                            output_seq_hash[end_node]  = all_reads[end_node][ int(data_l[10]):  ]
  
                    elif int(data_l[0]) - int(data_l[1]) ==1 and data_l[4] =="0" and data_l[8]=="0":
                        if int(data_l[11])  - int(data_l[10]) <100 and  int(data_l[5])<100:
                            output_seq_hash[end_node]  = all_reads[end_node][ int(data_l[6]):  ]                        
                        

            
            
            end_sequence = all_reads[0]
            top_number = max( output_seq_hash  )
            

            for x in xrange( 1,top_number+1  ):
                end_sequence +=output_seq_hash[x]


            OUTPUT.write(">%s\t%s\n%s\n"%( 
                line_l[0], line_l[-1],end_sequence   
            )
                         )    
            STATUS.write("%s\t%s\t%s\n"%( 
                            line_l[0], line_l[-1].strip(),len(
                                re.sub("\s+","",end_sequence)
                            )
                        )
                                     )  
            



if __name__=='__main__':
    usage = '''usage: python2.7 %prog [options]
transfer trim overlap relationship'''
    parser = OptionParser(usage =usage )

    parser.add_option("-i", "--INPUT", action="store",
                      dest="inp", 
                      help="Input overlap") 


    parser.add_option("-o", "--out", action="store",
                      dest="output",
                      help="The output name you want!!") 

    parser.add_option("-u", "--uni", action="store",
                      dest="unitig",
                      help="Raw unitig sequence in fasta !!")


    (options, args) = parser.parse_args()
    inp = options.inp
    output = options.output
    unitig = options.unitig

    ##############################################################
    ##############################################################
    ##############################################################
    #store all sequence to a hash to prepare for output
    root_path = os.getcwd()
    all_raw_seq_hash,max_length =Get_AllReads(unitig)
        


    RAW = open(inp  ,'rU' ) 
    OUTPUT = open(output,'w')
    Single_Assembly(RAW, OUTPUT,all_raw_seq_hash)
