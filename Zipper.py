#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/19


from lpp import *
import os

from optparse import OptionParser

def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option(
        "-q", "--Query", action="store",
        dest="query",
        help="Raw Reads in Fasta Format!!!"
    )
    
    parser.add_option(
        "-m", "--Ref", action="store",
        dest="reference",
        help="reference sequence in Fasta Format!!!"
    )
    
    parser.add_option(
	"-e", "--Exclude", action="store_true",
	dest="exclude",
        default = False,
	help="Exclude Contigs from reference and then assembly Other contigs!!!"
    )	    



    parser.add_option(
        "-i","--Identity",action= "store",
        dest = "identity",
        type="float",
        default=0.95,
        help="Identity!"
    )		

    parser.add_option(
        "-o","--OUT",
        action= "store",
        dest = "output",
        help="output file"
    )		
    parser.add_option(
        "-l",
        "--LENGTH",
        action= "store",
        dest = "length",
        type="int",
        default=1000,
        help="Overlap Length"
    )	
    parser.add_option(
        "-a",
        "--Assembly",
        dest="assembly",
        action = "store_true",
        default = False,
        help="Assembly?"
    )	
    parser.add_option(
        "-r",
        "--Reassembly",
        dest="reassembly",
        action = "store_true",
        default = False,
        help=" Alle Deletion"
    )	
    parser.add_option(
        "-c",
        "--Circular",
        action = "store_true",
        dest="circular",
        default = False,
        help="Guess Circluar"
    )		

    (options, args) = parser.parse_args()
    return options,args
if __name__=="__main__":
    options,args = get_para()
    reassembly = options.reassembly
    query = options.query
    identity = options.identity
    exclude = options.exclude
    output = options.output
    name =  os.path.splitext(query)[0]
    overlap_length = options.length
    assembly = options.assembly
    circluar = options.circular
    ref =  options.reference

    all_name = name+".all.fasta"
    format_name = name+".format.fasta"
    format_Reads_command = '''DB_Reads -i %(reads)s  -f %(name)s  -o %(out)s -r %(all)s'''%( 
        {
            "reads":query,
            "out":format_name,
            "all":all_name,
            "name":"Query"

        }
    )
    os.system(format_Reads_command)

    buildDB_Command = '''fasta2DB Reads %(reads)s '''%( 
        {
            "reads":format_name
        }    
    )	
    os.system(buildDB_Command)

    splitDB_Command = '''DBsplit Reads'''    
    os.system(splitDB_Command)

    SeqAlign_Command = '''HPC.daligner -v -B40 -T32 -t16 -e%s  Reads | csh -v '''%(identity)

    os.system( SeqAlign_Command )
    MergeAlign_Command = '''LAmerge  Alignment Reads*.las && rm Reads*.las'''
    os.system(MergeAlign_Command)
    SortAlign_Command = '''LAsort  Alignment && mv Alignment.S.las Alignment.las''' 
    os.system(SortAlign_Command)
    LA4Falcon_Command = '''LA4Falcon -mog Reads  Alignment >Alignment.m4''' 
    os.system(LA4Falcon_Command)

    os.system("rm Reads.db ")
    os.system("rm .Reads.*")

    Filter_Command = "DAFilter -i Alignment.m4 -o FilterAlignment.m4"

    os.system(Filter_Command)

    Transitive_Command = "Transitive_Remove -i FilterAlignment.m4  -l %s -g OVL -o Graph.detail"%(overlap_length)
    os.system(Transitive_Command)
    need_assembly = ["%s.unitig.detail"%(output)]
    need_assembly.append( "%s.unitig.Plasmid"%(output) )
    Contig_Generate = "Generate_Contig.py  -e OVL.edges  -n OVL.nodes  -o ./%s.unitig"%(output)
    os.system( Contig_Generate )
    if reassembly:
	Contig_Generate = "Generate_Contig.py -r -e OVL.edges  -n OVL.nodes  -o ./%s"%(output)
	os.system(Contig_Generate)
	need_assembly.append( "%s.Alle.detail"%(output) )
    if circluar:
	if reference and exclude:
	    Contig_Generate = "Generate_Contig.py -r -e OVL.edges  -n OVL.nodes  -o ./%s"%(output)
	    Unitig_Generate = "Generate_Unitig -f %s  -i Graph.detail -o Unitig_element.fasta"%( all_name  )
	    Assembly_Generate = " Assembly_ThroughUnitig.py  -i ./%s  -r %s  -o ./%s -u Unitig_element.fasta  " %( "%s.Alle.detail"%(output),all_name, "%s.Alle"%(output) )
	    os.system(Contig_Generate)
	    os.system(Unitig_Generate)
	    os.system(Assembly_Generate)

	    format_Ref_command = '''DB_Reads -i %(reference)s  -f ref  -o ref_format.fasta -r ref_all.fasta && fasta2DB Ref ref_format.fasta && rm ref_format.fasta  && rm ref_all.fasta  '''%( 
		{
		    "reference":ref,

		}
	    )	 
	    os.system(format_Ref_command)
	    
	    format_Contig_command = '''DB_Reads -i %s  -f Contig  -o contig_format.fasta -r contig_all.fasta && fasta2DB Contig contig_format && rm  contig_format.fasta && rm contig_all.fasta '''%( 
		"%s.Alle.fasta"%(output)
	    )	
	    os.system(format_Contig_command)
	    
	    SeqAlign_Command = '''HPC.daligner -v -B40 -T32 -t16 -e%s  Contig Ref  | csh -v '''%(identity)
	    os.system(SeqAlign_Command)
	    LA_RUN_Command  = " LA4Falcon  -mog   Ref  Contig  Ref.Contig.las | grep contains|cut -f 2 -d ' '| uniq > ref.list"
	    os.system(LA_RUN_Command)
	    
	    
	Contig_Generate = "Generate_Contig.py -c -r -e OVL.edges  -n OVL.nodes  -o ./%s"%(output)
	os.system(Contig_Generate)
	need_assembly.append( "%s.Alle.Plasmid"%(output) )		
    if assembly:
	Unitig_Generate = "Generate_Unitig -f %s  -i Graph.detail -o Unitig_element.fasta"%( all_name  )
	os.system(  Unitig_Generate )
	for key in need_assembly:
	    Assembly_Generate = " Assembly_ThroughUnitig.py  -i ./%s  -r %s  -o ./%s -u Unitig_element.fasta  " %( key,all_name, key )

	    os.system(Assembly_Generate)








