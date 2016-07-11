#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2016/6/12
"""

from lpp import *
kmer_index = Ddict()
def get_kmer(name,seq,kmer):
    global kmer_index
    seq = re.sub("\s+","",seq)
    rev_seq = complement(seq)
    
    for each_seq in [seq,rev_seq]:
        for i in xrange(kmer,len(each_seq)):
            kmer_index[ each_seq[i-kmer:i]  ][name] = ""

RAW = fasta_check( open(sys.argv[1])  )
for t,s in RAW:
    t = t.split()[0][1:]
    get_kmer(t,s,17)
OUTPUT = open("Hash.txt",'w')
for key,values in kmer_index.items():
    OUTPUT.write(key+'\t'+'; '.join( values )+'\n'  )
    
    