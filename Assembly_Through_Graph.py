#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/8/8

from lpp import *
import shutil
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
    all_data = {}
    DATA = fasta_check(open(file_name,'rU') )
    for t,s in DATA:
        s = re.sub("\s+",'',s)
        s_ = complement(s)
        name =t[1:].split()[0]
        all_data[name+'+']=s
        all_data[name+'-']=s_
        
    return all_data

def Single_Assembly(RAW,OUTPUT,all_raw_seq_hash,overlap):
    #store all sequence to a hash to prepare for output
    root_path = os.getcwd()

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
        else:
            contig_list = line_l[1].split("; ")
            end_sequence = all_raw_seq_hash[contig_list[0]]
            for i in xrange(1,len(contig_list)):
                query_Id = contig_list[i-1];subject_Id = contig_list[i]
                location= Find_Overhang(query_Id, subject_Id, 
                                       overlap)

                end_sequence+= all_raw_seq_hash[subject_Id][location:]
            if line_l[-1]=="Plasmid":
                end_sequence =Circulation(end_sequence)
            OUTPUT.write(">%s\t%s\n%s\n"%( 
                line_l[0], line_l[-1],end_sequence   
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
    parser.add_option("-v", "--OVL", action="store",
                      dest="overlap",
                      help="OverlapStore Location")    

    (options, args) = parser.parse_args()
    inp = options.inp
    output = options.output
    unitig = options.unitig
    overlap = options.overlap
    ##############################################################
    ##############################################################
    ##############################################################
    #store all sequence to a hash to prepare for output
    root_path = os.getcwd()
    all_raw_seq_hash =Get_AllReads(unitig)



    RAW = open(inp  ,'rU' ) 
    OUTPUT = open(output,'w')
    Single_Assembly(RAW, OUTPUT,all_raw_seq_hash,overlap)