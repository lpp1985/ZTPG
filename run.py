#!/usr/bin/python
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


    parser.add_option("-g", "--GKP", action="store",
                      dest="gkp",
                      help="gatekeeper directory")



    parser.add_option("-u","--UNI",action= "store",
                      dest = "uni",
                      help="Unitig directory"
                      )

    parser.add_option("-c","--REF",action= "store",
                      dest = "reference",
                      help="Reference sequence fasta format!"
                      )	
	
    parser.add_option("-o","--OUT",action= "store",
                      dest = "output",
                      help="output file"
                      )			
    parser.add_option("-v","--OVLA",action= "store",
                      dest = "overlap",
                      help="overlap store location!!"
                      )			

    (options, args) = parser.parse_args()
    return options,args
if __name__=='__main__':
    print( colored(  "Step1 Preparing!!",'blue')   )
    options,args = get_para()
    gkp = options.gkp

    uni = options.uni
    overlap = options.overlap

    reference = options.reference

    output = options.output
    cache_path = './cache/'
    if not  os.path.exists(  cache_path  ):
        os.mkdir(  cache_path )
    print ( colored( "Preparing ok!!",'green' )  )
    print( colored(  "Step1 Get best reads!!!!",'blue' )  )
    best_output = cache_path+'best.fasta'
    best_reads_command = cele_path+'''/get_best_reads.py -g %(gkp)s -b %(unig)s -o %(best)s'''%( 
        {
            'unig':uni,
            'best':best_output,
            "gkp":gkp
        } 
                                                                                                  )

    err = subprocess.Popen(  shlex.split( best_reads_command ),stderr=subprocess.PIPE  ).communicate()
    if not err[0]:
        print( colored("Extracting best reads OK!!","green")  )
    else:
        print(colored(err[0],'red'))
        print( colored('Step1 Error!','red') )
        #sys.exit()    

    ##开始进行参考图的构建
    print(  colored("Step2 Align best reads to Reference. Running!!" ,'blue')    )
    reference_output = cache_path+'reference_graph'

    reference_commandline = cele_path+'''/celera_blat.py -r %(reference)s -b %(best_reads)s -o%(out)s'''%( 
        {
            'reference':reference,
            'best_reads':best_output,
            'out':reference_output
        }
    )

    err = subprocess.Popen(  shlex.split( reference_commandline ),stderr=subprocess.PIPE  ).communicate()
    if  not err[0]:
        print( colored("best reads alignment OK!!",'green')  )
    else:
        print(err[0])
        print( 'Step2 Error!' )
        sys.exit()	










    #开始运行图整合算法 Integrate_Assembly
    #开始进行参考图的构建
    print(  colored("Step3 Reference Integrated Assembly Start!!" ,'blue')    )
    integrated_output = output

    intergate_commandline = cele_path+'''/Integrate_Assembly.py -c %(reference)s -u %(unitig)s -o %(out)s  -v %(overlap)s'''%( 
        {
            'reference':reference_output,
            'unitig':uni,
            'out':integrated_output,
            "overlap":overlap,
        }
    )
    print(intergate_commandline)
    err = subprocess.Popen(  shlex.split( intergate_commandline ),stderr=subprocess.PIPE  ).communicate()
    if  not err[0]:
        print( colored("Reads Integrated Okay!",'green')  )

    else:
        print(err[0])
        print( 'Step3 Error!'  )
	   
 
    #对矫正的结果进行拼接
    print(  colored('Step4 Assembly Contig !!','blue')   )
    assembly_output = output
    assembly_commandline = cele_path+'''/Assembly_Through_Graph.py -i %(output)s.detail -o %(output)s.fasta -u %(bes)s -v %(overlap)s  '''%( 
        {
            "output":output,
            "bes":best_output,
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
        
        
    