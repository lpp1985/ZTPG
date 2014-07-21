#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2014/4/9
from Dependency import *
Assembled_Contig_no = 1
status = 0







def Mummer_parse(  file_name  ):
    """运行nucmer并且根据show-coords的数据对所有的结果进行解析
    得到Contain，BEGIN，END，Identity的数据并将自身比自身的序列去除。而后，将这些数据分门别类放到一个多维哈希
    output_category中，其中一维键为tag，二维键是行

    """
    #运行nucmer
    output_category = Ddict()
    os.system(  "nucmer --maxmatch %(genome)s  %(genome)s -p cache"%( {"genome":file_name }  )  )
    align_data = os.popen(  """show-coords  cache.delta -odTl -L 40  | grep -P  "\[\S+\]$" """      )
    align_data.next()
    for line in align_data:
        line_l = line.strip().split("\t")

        identy,refname,queryname,tag  = Get_list( line_l,[6,11,12,13]   )
        if refname ==queryname:
            continue
        if float(  identy  )<90:
            continue
        name = re.search( "\[(\w+)\]",tag  ).group(1)
        output_category[ name  ][ line ] = ''

    return output_category



def Relation_parse(  file_name ,output_category   ):
    """
    接受所有的ContigID
    根据Mummer_parse获得的结果，对identity的节点，和contain的节点进行删除，取长的保留。
    而后将保留的节点根据Begin和END的关系构建overlap图
    对获得的Contig图进行修订用_Trim函数
    该函数的作用如下：
    如果 a-->b b-->c 并且 a-->c
+          ----------------------------------
    -------------------
             -----------------------------------------------
    这种情况会导致双向唯一过敏感，
    纠正的方法是：
    如果某一个节点的下游开叉，
    遍历开叉下游节点，对开叉下游节点的连接关系进行遍历，如果下下游节点存在于上上游节点的下游关系中，则将该关系删除






    """
    global  name_prefix












    def _Trun_contain_Rela(G_start,contain_rela):

        G = deepcopy(G_start)
        for big in contain_rela:
            if big in  G_start.succ:
                big_succ = set(G_start.succ[big])
            else:
                big_succ=set([])

            if big in G_start.pred:
                big_pred =set( G_start.pred[big] )
            else:
                big_pred =set([])
            for small in contain_rela[big]:

                if small in  G_start.succ:
                    small_succ = set(G_start.succ[small] )
                else:
                    small_succ=set([])

                if small in G_start.pred:
                    small_pred = set( G_start.pred[small] )
                else:
                    small_pred =set([])				
                if small_succ<=big_succ and small_pred <=big_pred:
                    G.remove_bi_node(small)
                #if big =="XV05_100+":
                    #print(big,small)
                    #print(big_succ,small_succ)
                    #print(big_pred,small_pred)


        return G



    #检查contain关系，并将所有contain的节点删除

    containeed_line = {}

    #首先对所有的reads做筛选，将contain和完全相同的去除掉

    #检查contain关系，并将所有contain的节点删除
    CONTAIN = open( name_prefix+'.contains','w'  )
    containeed_line = {}
    CONTAIN.write( "Contig\tIncluded_by\n"  )
    #从图中去除所有的contain关系，如果这两个关系的上下游都一样，则讲这个节点替换为大节点,contain_rela记录所有的包含关系，这类关系最后通过图
    #的结构进行削减，如果小的overlap关系和大的overlap关系完全相同，则将该节点删除


    contain_rela = Ddict()
    for each_line in output_category[ "CONTAINS"  ]:
        line_l = each_line.strip().split("\t")
        big_contig,small_contig = Get_list( line_l,[11,12] )
        frame = line_l[10]
        if frame =="-1":
            frame ="-"
        else:
            frame ='+'
        contain_rela[big_contig+'+'][small_contig+frame] = ""
        #CONTAIN.write( small_contig+'\t'+big_contig+'\n'   )
    #检查contained关系
    for each_line in output_category[ "CONTAINED"  ]:
        line_l = each_line.strip().split("\t")
        big_contig,small_contig = Get_list( line_l,[12,11] )
        frame = line_l[10]
        if frame =="-1":
            frame ="-"
        else:
            frame ='+'		
        contain_rela[big_contig+frame][small_contig+"+"] = ""
        #CONTAIN.write( small_contig+'\t'+big_contig+'\n'   )

    for data in containeed_line:
        CONTAIN.write(data)
    #检查identity
    #print(len( output_category[ "IDENTITY"  ]))
    for each_line in output_category[ "IDENTITY"  ]:

        line_l = each_line.strip().split("\t")
        query_length,subject_length,frame,query_contig,subject_contig = Get_list( line_l,[7,8,10,11,12] )
        query_length =int( query_length );subject_length = int( subject_length )
        query_contig = query_contig+"+"
        if frame=="-1":
            frame ="-"
        else:
            frame ="+"
        subject_contig = subject_contig+frame
        if query_length>subject_length:
            small_contig = subject_contig
            big_contig = query_contig
        elif query_length==subject_length:
            big_contig,small_contig = sorted([query_contig,subject_contig]) 
        else:
            small_contig = query_contig
            big_contig = subject_contig

        contain_rela[big_contig][small_contig] = ""
        CONTAIN.write( small_contig+'\t'+big_contig+'\n'   )			
        print(big_contig, small_contig)
    #print(contain_rela) 
    #开始对 Start和END进行解析，期间只要碰到 删除的节点，就跳过
    #设置一个初始图
    G_contig_init = Contig_Graph()
    # 添加所有的节点 添加双向
    FASTA = fasta_check(open( file_name ,'rU') )
    for t,s in FASTA:
        each_contig = t.strip()[1:].split()[0]

        for direction in ['-','+']:
            G_contig_init.add_node( each_contig+direction,name = each_contig+direction )

    #根据Begin和END添加关系
    #根据BEGIN进行构图
    for each_line in output_category[ "BEGIN"  ]:
        line_l = each_line.split("\t")
        query_node,subj_node,frame = Get_list( line_l,[ 11,12,10 ]  )
        #如果删除的节点出现了这些数据则跳过
        #否则
        if frame =="1":
            direction = "+"
        else:
            direction = '-'

        G_contig_init.add_bi_edge(  subj_node+direction, query_node+'+'    )




    #根据END进行构图
    for each_line in output_category[ "END"  ]:
        line_l = each_line.split("\t")
        query_node,subj_node,frame = Get_list( line_l,[ 11,12,10 ]  )
        #如果删除的节点出现了这些数据则跳过
        #否则
        if frame =="1":
            direction = "+"
        else:
            direction = '-'

        G_contig_init.add_bi_edge( query_node+'+', subj_node+direction    )








    #修图，将tiling边删除
    #print(contain_rela)
    G_contig_init = _Trun_contain_Rela(G_contig_init, contain_rela)

    G_Trimed = Transitive_Remove( G_contig_init )


    #双向图变成单向图
    ##首先，将singleton的反向节点删除
    Remove_rev_Singleton(G_Trimed)

    #得到新的最终的Graph


    return G_Trimed
    ##到目前为止 G_Trimed完成，下面遍历所有的contig，遍历标准是predecessor 为1，successors为1，认为是一个contig
    ##见这些contig的明细信息保存下来

def Parse_Contig( contig_file  ):
    """解析contig文件，生成参考序列网络"""
    CONTIG = open( contig_file,'rU' )
    G_ref = nx.DiGraph()

    for line in CONTIG:
        if line.startswith( "##" ):
            last = ''
            continue
        elif line.startswith( "#" ):
            tag = "+"
            if "[RC]" in line :
                tag = "-"
            name = re.search( "^\#([^\(]+)",line ).group(1)
            if name not in unique_contig:
                continue
            name = name+tag
            G_ref.add_node( name   )
            if last:
                G_ref.add_edge(   last,name    )
            last = name

    return G_ref


def Coverage_count(COVERAGE):
    all_coverage = []
    for t,s  in fasta_check( COVERAGE  ):
        cov_list = [int (x) for x in s.split()]
        all_coverage.extend(cov_list)

    cov_median = np.median(all_coverage)
    stand = np.std(all_coverage)

    output_cov = cov_median*1.5
    return output_cov



if __name__=='__main__':
    name_prefix = "lpp"
    raw_file = sys.argv[1]
    output_category = Mummer_parse( raw_file  )

    G_Contig= Relation_parse( raw_file, output_category )



    root_path = os.getcwd()
    if not os.path.exists(  root_path+'/css' ):
        shutil.copytree( cele_path+'/Template/css', root_path+'/css'  )

    if not os.path.exists(  root_path+'/js' ):
        shutil.copytree( cele_path+'/Template/js', root_path+'/js'  )    
    templeloader = FileSystemLoader(cele_path+"/Template")
    env = Environment(loader = templeloader)
    template = env.get_template('template.html')

    END = open(  "web.html",'w' )

    web_data = json_graph.node_link_data(G_Contig)

    END.write(
        template.render(

            raw_links = json.dumps(web_data['links']    )  ,
            raw_nodes = json.dumps(web_data['nodes']   )  
        )
    )


    #区分contig为但个的contig和多个的contig
    FASTA = fasta_check( open( sys.argv[1],'rU' )   )
    PLASMID = open( name_prefix+'.PLASMID' ,'w' )
    unique_contig = {}
    coverage_thre = Coverage_count(open(sys.argv[3],'rU')   )	
    for t,s in FASTA:
        if "circular" in t:
            PLASMID.write( t+s )
        coverage = re.search( "cov\=(\d+)",t ).group(1)
        if int(coverage) <coverage_thre:
            name = t[1:].split()[0]
            unique_contig[ name ] = ''


    G_ref = Parse_Contig( sys.argv[2]  )
    MAPPING  = open( name_prefix+".Mapping" ,'w'  )
    MAPPING.write("Contig\tDetail\tCategory\n")
    #根据reference进行gap填补和组装
    for each_node in G_ref:
        succ = G_ref.successors(each_node)

        if succ:
            succ = succ[0]
            G_Contig.check_path(each_node,succ, unique_contig)
    #防止Gap引起的误拼    
    removed_edge = []
    for edge in G_Contig.edges():
        edge_data = '; '.join(edge)
        if not re.match( "New\d+" ,edge_data ):
            removed_edge.append(edge)  
    for edge in removed_edge:
        G_Contig.remove_bi_edge(edge[0],edge[1])


    New_assembly_commandline =shlex.split( "./Post_assembly.py -u %s -r %s -o Reference_addtion"%(sys.argv[1], MAPPING.name ) )

    subprocess.check_output(New_assembly_commandline)
    NEW_CONTIG_REF_ADD = open(name_prefix+".NewContig",'w')
    NEW_CONTIG_REF_ADD.write( open(sys.argv[1]).read() )
    NEW_CONTIG_REF_ADD.write( open("Reference_addtion.Contigs",'rU').read() ) 


    template = env.get_template('template.html')
    END2 = open(  "web2.html",'w' )
    web_data = json_graph.node_link_data(G_Contig) 
    END2.write(
        template.render(

            raw_links = json.dumps(web_data['links']    )    ,
            raw_nodes = json.dumps(web_data['nodes']   )  
        )
    )
    
    DETAIL =  open(name_prefix+'.assembly_detail', 'w') 
    DETAIL.write("Contig\tDetail\tCategory\n")
    Contig_relation,plasmid_contig ,G_Output = Get_Contig(G_Contig)
    Final_assembly_commandline =shlex.split( "./Post_assembly.py -u %s -r %s -o Reference_Final"%(NEW_CONTIG_REF_ADD.name, DETAIL.name ) )

    subprocess.check_output(Final_assembly_commandline)    