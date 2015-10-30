#!/usr/bin/python
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
import shlex

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
            assembly_path = './assembly_new/'

            cache_path = assembly_path+line_l[0]+'/'
            check_path(  cache_path   )
            CACHE_READS = open(    cache_path+'reads.fasta','w'  )
            for each_data in contig_list:
                i+=1
                CACHE_READS.write('>%s\n%s\n'%(i,all_raw_seq_hash[  each_data  ] ) )
                all_reads[i] = all_raw_seq_hash[  each_data  ]

            os.system(
                '''nucmer --maxmatch --forward    %(query)s %(query)s -p %(out)s >/dev/null 2>&1'''%(
                    {
                        "query":CACHE_READS.name,
                        "out":cache_path+'/out'
                    }
                )
            )
            nucmer_out = os.popen(""" show-coords  -oHTd %(out)s.delta | grep -P  "\[[^B]"   """%(
                {
                    "query":CACHE_READS.name,
                    "out":cache_path+'/out'
                }
            )
                                  )
            top_number= i
            str_graph = nx.DiGraph()
            end_sequence = all_reads[1]
            
            for data in nucmer_out:

                data_l = data.split("\t")

                start_node = int(data_l[-3])
                end_node = int(data_l[-2])
                if start_node>=end_node:
                    continue
                str_graph.add_edge(
                    start_node,end_node,

                    seq=all_reads[end_node][ int(data_l[3]):  ]
                )
            assm_paths = [1]
            m=1
            need_delete = {}
            for key in str_graph:
                if not str_graph.predecessors(key):
                    if key !=1:
                        need_delete[key] = ""
                if not str_graph.successors(key):
                    if key !=top_number:
                        need_delete[key] = ""
            print(line_l[0],+'\t'+"\t".join(need_delete)+" is delete!!!")
            
            if len(need_delete):
                str_graph.remove_nodes_from(  need_delete.keys() )
            while m<top_number:
                try:
                    new_s = min([x for x in  str_graph[m] if x >m])
                    assm_paths.append(new_s)
                    m = new_s            
                except:
                    print(line_l[0]+"is Error!!!")
                    
                    
                    
            print("%s is Assembling"%(line_l[0]))
            
            print("Path is %s !!!!"%("->".join(assm_paths)))
            print("##################################")
            print("##################################\n\n\n\n\n")
            for k in xrange(1,len(assm_paths)):
                end_sequence +=  str_graph[ assm_paths[k-1] ][ assm_paths[k] ][ "seq"  ]
             
            #if line_l[-1]=="Plasmid":

                #end_sequence =Circulation(end_sequence)
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
