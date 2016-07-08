#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2016/6/13
"""

from Dependency import *
def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option("-i", "--Input", action="store",
                      dest="fasta",
                      help="Contig Sequence in Fasta Format")

    parser.add_option("-o","--Ouptut",action= "store",
                      dest = "output",
                      help=" Result Suffix "
                      )
    parser.add_option("-p","--Pacbio",action= "store",
                      dest = "pacbio",
                      help=" Pacbio Reads "
                      )    


    (options, args) = parser.parse_args()
    return options,args

if __name__ == '__main__':
    options,args = get_para()
    out_path = os.path.dirname(os.path.abspath(options.output))
    
    raw_file = options.fasta
    output_category = Mummer_parse( raw_file  )
    
    G_Contig= Relation_parse( raw_file, output_category, options.output,contain_trim=0 )    
    name = out_path.split("/")[-1]
    
    #nx.single_source_shortest_path_length(G_Contig)
    #os.system(   "nucmer --maxmatch %s %s -p %s/Pacbio"%( options.pacbio,options.fasta,out_path   )   )
    
    all_ref_data = os.popen( "show-coords -orlTH %s/Pacbio.delta"%(out_path)  )
    all_ref_nodes = {}
    all_sorted_nodes = []
    for line in all_ref_data:
        line_l = line[:-1].split("\t")
        q_start = int(line_l[2])
        q_end = int(line_l[3])
        if q_start >q_end:
            tag = '-'
        else:
            tag = '+'
        q_length = int(line_l[8])
        q_name = line_l[-2]
        all_ref_nodes [ q_name ] = ""
        if q_length>1000 and  line_l[-1] in ["[CONTAINS]","[IDENTITY]","[CONTAINED]"]:
            if line_l[-1] in ["[IDENTITY]","[CONTAINED]"]:
                all_sorted_nodes = [q_name+tag ]
                break
            else: 
                all_sorted_nodes.append( q_name+tag  )
                
    if len(all_sorted_nodes)==1:
        OUTPUT = open(options.output,'w')
        ALL_SEQ= fasta_check(open(options.fasta,'rU'))
        need_name = all_sorted_nodes[0][:-1]
        for t,s in ALL_SEQ:
            
            if t.strip().split()[0][1:] ==need_name:
                
                OUTPUT.write(">%s\n%s"%(name,s))
                sys.exit()
    try:
        new_path = nx.shortest_path( G_Contig,all_sorted_nodes[0],  all_sorted_nodes[-1]  )
    
    except:
        try:
            new_path = nx.shortest_path( G_Contig,all_sorted_nodes[0],  all_sorted_nodes[-2]  )
        except:
            try:
                new_path = nx.shortest_path( G_Contig,all_sorted_nodes[1],  all_sorted_nodes[-2]  )
            except:

                new_path = nx.shortest_path( G_Contig,all_sorted_nodes[1],  all_sorted_nodes[-1]  )    
    END = open("%sNew_path.list"%(out_path),'w')
    
    END.write('%s\t'%(name)+"; ".join(new_path)+'\tDoubt\n')
    os.system(  "Assembly_by_Nucmer.py  -i %s  -o %s -u %s/Reads.fasta"%(END.name,options.output,out_path)  )
    #removed_node = {}
    #for node in G_Contig.nodes():
        #if node[:-1] not in all_ref_nodes:
            #removed_node[ node[:-1] ] = ""
            
    #for key in removed_node:
        #G_Contig.remove_bi_node(  key )
        
    
