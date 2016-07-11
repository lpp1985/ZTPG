#!/usr/bin/env python
#coding:utf-8
"""
  Author:   -->
  Purpose: 
  Created: 2016/6/12
"""

from lpp import *
import os

def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option("-k", "--Kmer", action="store",
                      dest="kmer",
                      help="Kmer Sequence Database")

    parser.add_option("-o","--Ouptut",action= "store",
                      dest = "output",
                      help=" Result Suffix "
                      )
    parser.add_option("-s","--Super",action= "store",
                      dest = "superreads",
                      help=" SuperReads "
                      )    
    parser.add_option("-p","--Pacbio",action= "store",
                      dest = "pacbio",
                      help=" Pacbio Reads "
                      )    


    (options, args) = parser.parse_args()
    return options,args


if __name__ == '__main__':
    options,args = get_para()
    sorted_pacbio_data = Ddict()
    all_superreads = {}
    for t,s in fasta_check( open( options.superreads,'rU' )  ):
        all_superreads[ t[1:].split()[0]  ] = t+s
    SEQ = fasta_check(open(  options.pacbio  ))
    for t,s in SEQ:
        s = re.sub("\s+","",s)
        sorted_pacbio_data[ len(s) ][ t,s ]=""
    data_seq =Ddict()
    for line in open( options.kmer ,'rU'):
        line_l = line.strip().split("\t")
        all_data = line_l[1].split("; ")
        for key in all_data:
            data_seq[ line_l[0] ][key] = ""
    output_path = "./Cache/"
    m=0
    for length in sorted(sorted_pacbio_data)[::-1]:
	if length <9000:
            continue
        for t,s in sorted_pacbio_data[ length ]:
            all_need_reads = {}
            seq = s
            rev_seq = complement(seq)
            m+=1
            cache_path = output_path+'/%s/'%(m)
            if not os.path.exists(cache_path):
                
                os.makedirs( cache_path )
            PACBIO = open(cache_path+'/Pacbio.fasta','w')
            PACBIO.write(t+s)
            READS = open(cache_path+'/Reads.fasta','w')
            LIST = open(cache_path+'/Reads.list','w')
            for each_seq in [seq,rev_seq]:    
                for i in xrange(17,len(each_seq)):
                    kmer = each_seq[i-17:i]
                    for each_reads in data_seq[ kmer ]:
                        all_need_reads[ each_reads  ] = ""
                        
            for name in all_need_reads:
                READS.write(all_superreads[name])
                LIST.write( name+'\n' )
        
