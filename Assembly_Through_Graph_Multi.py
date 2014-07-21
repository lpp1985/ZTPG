#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: Multiprocess assembly of genome data
  Created: 2014/7/2
"""
from Dependency import *
from lpp import *
from multiprocessing import Pool
from Assembly_Through_Graph import *
result_path = "./result_cache/"
cache_path = "./split_cache/"
import subprocess
if not os.path.exists(result_path):
    os.makedirs(result_path)
if not  os.path.exists(cache_path):
    os.makedirs(cache_path)
def Assembly(number):
    
    RAW = open(cache_path+"%s.detail"%(number),'rU')
    OUTPUT = open(result_path+'%s.result'%(number),'w')
    Single_Assembly(RAW, OUTPUT,all_raw_seq_hash,overlap)

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

    parser.add_option("-n", "--number", action="store",
                      dest="number",
                      type='int',
                      help="Number of Process you want!!")	
    parser.add_option("-v", "--OVL", action="store",
                      dest="overlap",
                      help="OverlapStore Location")  
    
    parser.add_option("-a", "--Already", action="store",
                      dest="already",
                      help="already_assembled")   
    

    (options, args) = parser.parse_args()
    inp = options.inp
    output = options.output
    reads = options.unitig
    number = options.number
    overlap = options.overlap
    all_raw_seq_hash =Get_AllReads(reads)

    i=1
    split_hash = {}
    already_have = {}
    ALREADY = fasta_check(open(options.already,'rU'))
    for t,s in ALREADY:
        already_have[t[1:].split()[0]] = ''
        END.write(t+s)
    END = open(output,'w')
    for line in open(inp,'rU'):
        name = line.split("\t")[0]
        if name in already_have:
            continue
        nu = i%number
        if nu not in split_hash:
            split_hash[nu] = open(cache_path+"%s.detail" %(nu),'w')
        split_hash[nu].write(line)
        i+=1
    pool = Pool(number)
    #map(Assembly,split_hash)
    pool.map(Assembly,split_hash)

    for each_f in glob.glob(result_path+'*.result'):
        END.write(open(each_f,'rU').read())