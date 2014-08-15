#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2014/8/13
"""
from lpp import *
from optparse import OptionParser
from configure import *
def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option("-r", "--Ref", action="store",
                      dest="Ref",
                      help="Reference Squence in fasta format!")


    parser.add_option("-a","--Reads",action= "store",
                      dest = "Read",
                      help=" Reads in Fasta Format"
                      )

    parser.add_option("-o","--Ouptut",action= "store",
                      dest = "output",
                      help=" outputName"
                      )


    (options, args) = parser.parse_args()
    return options,args


if __name__ == '__main__':
    options,args = get_para()
    ref = options.Ref
    reads = options.Read
    out = options.output
    commandline="""#!%(amos)srunAmos -C
#? Use  

#? Usage:          
#?         Cons prefix \
#?		-D REFCOUNT=<n>         \       # Number of sequences in the 1st assembly ; (Required)
#?		-D OVERLAP=<n> 		\       # Assembly 1 vs 2 minimum overlap (Default 40bp)
#?		-D CONSERR=<f>		\	# Maximum consensus error (0..1) (Default 0.06)
#?		-D MINID=<n>		\	# Minimum overlap percent identity for alignments (Default 94)
#?		-D MAXTRIM=<n>			# Maximum sequence trimming length (Default 20bp)

#--------------------------------------- USER DEFINED VALUES ------------------#

REFCOUNT= 0
MINID   = 94
OVERLAP	= 40
MAXTRIM = 20
WIGGLE  = 15
CONSERR = 0.06

#------------------------------------------------------------------------------#
REF    = %(ref)s
READ   = %(read)s
REF_LIST = %(ref)s.list
READ_LIST  = %(read)s.read.list
TGT     = $(PREFIX).afg
BANK    = $(PREFIX).bnk
REFSEQ  = $(PREFIX).ref.seq
QRYSEQ  = $(PREFIX).qry.seq
ALIGN   = $(PREFIX).delta
COORDS  = $(PREFIX).coords
OVLTAB  = $(PREFIX).ovl
OVLAMOS = $(PREFIX).OVL
CONTIG  = $(PREFIX).contig
FASTA   = %(out)s

SINGLETONS    = $(PREFIX).singletons
SINGLETONSEQ  = $(PREFIX).singletons.seq

## Cat all data
1: cat $(REF) $(READ) >total_cache.fasta
## add quality
2: %(cele_path)sadd_quality.py total_cache.fasta total_cache.qual 20
## build afg
3: %(amos)stoAmos -s total_cache.fasta -q total_cache.qual -o  $(TGT)
## extract read list
4: grep '>' $(READ) |sed "s/>//g" -|sed -r "s/\s+\S+//g" - > $(READ_LIST)
## extract reference list
5: grep '>' $(REF) |sed "s/>//g" - | sed -r "s/\s+\S+//g" - > $(REF_LIST)

#------------------------------------------------------------------------------#

INPUTS  = $(TGT) $(REFCOUNT)
OUTPUTS = $(CONTIG) $(FASTA)

#------------------------------------------------------------------------------#

BINDIR=%(amos)s
NUCMER=%(nucmer)s
DELTAFILTER	= %(deltafilter)s
SHOWCOORDS	= %(showcoords)s

#------------------------------------------------------------------------------#

## Building AMOS bank & Dumping reads
10: rm -fr $(BANK)
11: $(BINDIR)/bank-transact -c -z -b $(BANK) -m $(TGT)
12: $(BINDIR)/dumpreads $(BANK) -E $(REF_LIST) -M $(REFCOUNT) > $(REFSEQ)
13: $(BINDIR)/dumpreads $(BANK) -E $(READ_LIST) -m $(REFCOUNT) > $(QRYSEQ)

## Getting overlaps 
20: $(NUCMER) -maxmatch -c $(OVERLAP) $(REFSEQ) $(QRYSEQ) -p $(PREFIX)
21: $(SHOWCOORDS) -H -c -l -o -r -I $(MINID) $(ALIGN) | $(BINDIR)/nucmerAnnotate | egrep 'BEGIN|END|CONTAIN|IDENTITY' > $(COORDS) 
22: $(BINDIR)/nucmer2ovl -ignore $(MAXTRIM) -tab $(COORDS) | $(BINDIR)/sort2 > $(OVLTAB)

## Converting overlaps
23: $(BINDIR)/ovl2OVL $(OVLTAB)  > $(OVLAMOS)

## Loading overlaps to the bank
24: rm -f $(BANK)/OVL.* 
25: $(BINDIR)/bank-transact -z -b $(BANK) -m $(OVLAMOS)

## Running contigger
30: rm -f $(BANK)/LAY.*
31: $(BINDIR)/tigger -b $(BANK)

## Running consensus
40: rm -f $(BANK)/CTG.*
41: $(BINDIR)/make-consensus -B -e $(CONSERR) -b $(BANK) -w $(WIGGLE) 



## Converting to FastA file
60: $(BINDIR)/bank2fasta -b $(BANK) > $(FASTA)


"""%(
       {
           "amos":amos,
           "ref":ref,
           "read":reads,
           "cele_path":cele_path,
           "nucmer":nucmer,
           "deltafilter":delta_filter,
           "showcoords":showcoords,
           "out":out
       }
   )
    COMMAND= open("cons","w")
    COMMAND.write(commandline)
    os.system("chmod  755 %s"%(COMMAND.name))