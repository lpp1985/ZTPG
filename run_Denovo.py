#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2013/7/19


from lpp import *
from  termcolor import colored
import subprocess,shlex
from optparse import OptionParser
from configure import cele_path
def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option("-i", "--Reads", action="store",
                      dest="reads",
                      help="Raw Reads in Fasta Format!!!")



    parser.add_option("-c","--REF",action= "store",
                      dest = "reference",
                      help="Reference sequence fasta format!"
                      )	
	
    parser.add_option("-o","--OUT",action= "store",
                      dest = "output",
                      help="output file"
                      )			

    (options, args) = parser.parse_args()
    return options,args
if __name__=='__main__':
    print( colored(  "Step1 Preparing!!",'blue')   )
    options,args = get_para()
    reads = options.reads


    reference = options.reference

    output = options.output
    cache_path = './cache/'
    if not  os.path.exists(  cache_path  ):
        os.makedirs(  cache_path )
    print ( colored( "Preparing ok!!",'green' )  )
    print( colored(  "Step1 Rename Reads",'blue' )  )
    format_reads = cache_path+'formatedreads.fasta'
    all_reads = cache_path+'allreads.fasta'
    best_reads_command = cele_path+'''/DB_Reads -i %(reads)s  -f Read  -o %(out)s -r %(all)s'''%( 
        {
            "reads":reads,
            "out":format_reads,
            "all":all_reads
        } 
                                                                                                  )

    err = subprocess.Popen(  shlex.split( best_reads_command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        print( colored("Extracting best reads OK!!","green")  )
    else:
        print(colored(err[0],'red'))
        print( colored('Step1 Error!','red') )
        #sys.exit()   
    
    print(  colored("Step2 Align all Reads Each Other to Detect Overlap" ,'blue')    )
    buildDB_Command = cele_path+'''/DAZZ_DB/fasta2DB Reads %(reads)s '''%( 
        {
            "reads":format_reads
        }    
    )
    err = subprocess.Popen(  shlex.split( buildDB_Command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        print( colored("Reads Build Database OK!!","green")  )  
    else:
        print(colored(err[0],'red'))
        print( colored('Step2  Reads Build  Error!','red') )    
        sys.exit()   
        
    splitDB_Command = cele_path+'''/DAZZ_DB/DBsplit Reads'''    
    err = subprocess.Popen(  shlex.split( splitDB_Command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        print( colored("Split Reads  Database OK!!","green")  )  
    else:
        print(colored(err[0],'red'))
        print( colored('Step2  Split Reads  Database Error!','red') )    
        sys.exit()    
        
        
        
        
    SeqAlign_Command = cele_path+'''/DALIGNER/HPC.daligner -v -B40 -T32 -t16 -e.95 -l1000 -s1000 Reads | csh -v '''  
    #os.system(SeqAlign_Command)
    #err = subprocess.Popen(  shlex.split( SeqAlign_Command ),stderr=subprocess.PIPE  ).communicate()
    #if not err[0]:
        #print( colored("Reads Self-Align   OK!!","green")  )  
    #else:
        #print(colored(err[0],'red'))
        #print( colored('Step2 Reads Self-Align  Error!','red') )    
        #sys.exit()   
    
    
    MergeAlign_Command = cele_path+'''/DALIGNER/LAmerge  Alignment Reads*.las'''    
    print(MergeAlign_Command)
    err = subprocess.Popen(  shlex.split( MergeAlign_Command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        #os.system("rm Reads*.las ")
        print( colored("Reads Self-Align Merge   OK!!","green")  )  
    else:
        print(colored(err[0],'red'))
        print( colored('Step2 Reads Self-Align Merge Error!','red') )    
        sys.exit()     
    
    SortAlign_Command = cele_path+'''/DALIGNER/LAsort  Merge'''    
    err = subprocess.Popen(  shlex.split( SortAlign_Command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        os.system("mv Merge.S.las Merge.las")
        print( colored("Reads Self-Align sort   OK!!","green")  )  
    else:
        print(colored(err[0],'red'))
        print( colored('Step2 Reads Self-Align Merge Error!','red') )    
        sys.exit()         

    
    LA4Falcon_Command = cele_path+'''/DALIGNER/LA4Falcon -mog Reads  Merge >Alignment.m4'''    
    err = subprocess.Popen(  shlex.split( LA4Falcon_Command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
       
        print( colored("Reads LA4Falcon  OK!!","green")  )  
    else:
        print(colored(err[0],'red'))
        print( colored('Step2 LA4Falcon Error!','red') )    
        sys.exit()         

    LAFilter_Command = cele_path+'''/DAFilter -i Alignment.m4 -o FilterAlignment.m4'''    
    err = subprocess.Popen(  shlex.split( LAFilter_Command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:

        print( colored("Reads LA4Filter  OK!!","green")  )  
    else:
        print(colored(err[0],'red'))
        print( colored('Step2 LA4Filter Error!','red') )    
        sys.exit()         










    
    #开始进行Contig构建
    print(  colored("Step3 Reference Integrated Assembly Start!!" ,'blue')    )


    contig_commandline = cele_path+'''/Generate_Contig.py -i FilterAlignment.m4  -o %(out)s  '''%( output )
    err = subprocess.Popen(  shlex.split( contig_commandline ),stderr=subprocess.PIPE  ).communicate()
    if  not err[0]:
        print( colored("Contig Generate Okay!",'green')  )

    else:
        print(err[0])
        print( 'Step3 Contig Generate Error!'  )
	   
 
    #对矫正的结果进行拼接
    print(  colored('Step4 Assembly Contig !!','blue')   )
    assembly_output = output
    assembly_commandline = cele_path+'''/Assembly_by_daligner.py -i %(output)s.detail -o %(output)s.fasta -u %(bes)s   '''%( 
        {
            "output":output,
            "bes":all_reads,
            "overlap":overlap
        }  
    )
    
    
    err = subprocess.Popen(  shlex.split( assembly_commandline ),stderr=subprocess.PIPE  ).communicate()
    
    if  not err[0]:
        print( colored("Running Successful!!",'green')  )
    else:
        print(colored(err[0],'red') )
        print( colored('Step4 Error!','red') )
        
    print(  colored('Step5 Guess Plasmid !!','blue')   )
    
    guess_commandline = cele_path+"""/Find_Potential_Cycle.py  -p %(out)s.graph -s %(out)s.fasta -o %(out)s.optimize"""%(
        {
            "out":output
        }
                                                                                                                         )
   
    err = subprocess.Popen(  shlex.split( guess_commandline ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        print(  colored("Running Successful!!",'green')  )
    else:
        print(colored(err[0],'red') )
        print( colored('Step5 Error!','red') )        
    
        sys.exit()		


    print(  colored('Step6 Addtional Assembly!!','blue')   )
    
    addtion_commandline = cele_path+"""/Addtional_Relation_Find.py  -i  %(out)s.fasta  -o %(out)s.addtional """%(
        {
            "out":output
        }
                                                                                                                         )
    
 
    err = subprocess.Popen(  shlex.split( addtion_commandline ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        print(  colored("Running Successful!!",'green')  )
    else:
        print(colored(err[0],'red') )
        print( colored('Step6 Error!','red') )        
    
        sys.exit()	
        
    print(  colored('Step7 Consensus Build!!','blue')   )
    print("Please choose which one you want to use as final result!")
    print(colored("1)Error-free Assembly result, the staistical infomation is:","green") )
    print(open(output+'.status').read() )
    print(colored("2)Topological Optimized Assembly result, the staistical infomation is:","green") )
    print(open(output+'.optimize.status').read() )
    print(colored("3)Redundency removal  Assembly result, the staistical infomation is:","green") )
    print(open(output+'.addtional.status').read() )
    choosed =""
    #for test
    #choosed ="2"
    
    while  choosed not in[ "1","2","3"]:
        choosed = raw_input("Please choose,1 or 2 or 3 ?")
    if choosed =="1":
        end_seq = output+".fasta"
    elif choosed =="2":
        end_seq = output+".optimize.fasta"
    else:
        end_seq = output+".addtional.fasta"

    
    consensus_commandline = cele_path+"""/Consensus_Build.py   -r  %(end_seq)s -a %(all_read)s  -o %(out)s.consensus.fasta """%(
            {
                "end_seq":end_seq,
                "out":output,
                "all_read":all_reads
            }
    )    
    os.system(consensus_commandline)
    os.system("./cons  final_consensus")
