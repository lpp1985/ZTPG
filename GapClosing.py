#!/usr/bin/python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2014/4/9


from copy import deepcopy
import subprocess
import shlex
from lpp import *
from  jinja2 import FileSystemLoader,Environment
import json
import networkx as nx
import numpy as np
Assembled_Contig_no = 1
status = 0
def Get_list(  has_list,location_list  ):
    #将对应的location的元素打入到输出列表中
    output_list = []
    for i in location_list:
        output_list.append( has_list[ i ]   )
    return output_list

def Mummer_parse(  file_name  ):
    """运行nucmer并且根据show-coords的数据对所有的结果进行解析
    得到Contain，BEGIN，END，Identity的数据并将自身比自身的序列去除。而后，将这些数据分门别类放到一个多维哈希
    output_category中，其中一维键为tag，二维键是行

    """
    #运行nucmer
    output_category = Ddict()
#	os.system(  "nucmer --maxmatch %(genome)s  %(genome)s -p cache"%( {"genome":file_name }  )  )
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
    则变成a-->b-->c，并将反向的链接关系也更新
    这样做的原因是防止双向唯一检验的假阳性
    如：
          ----------------------------------
    -------------------
             -----------------------------------------------
    这种情况会导致双向唯一过敏感，
    纠正的方法是：
    如果某一个节点的下游开叉，
    遍历开叉下游节点，对开叉下游节点的连接关系进行遍历，如果下下游节点存在于上上游节点的下游关系中，则将该关系删除






    """
    global  name_prefix

    def _Trim_node( G ):
        '''对于一些tiling结构进行修剪，遍历下游节点，如果下游节点的下游节点与上上游节点相连，
        则将该边删除
        '''
        G_output = deepcopy(G)
        isinstance( G_output,Contig_Graph  )
        isinstance(    G,Contig_Graph     )
        for node in G:
            if len( G.successors( node ) )>1:

                for each_child in G.successors(  node ):
                    for each_child_child in G.successors_iter( each_child  ):
                        if G.has_edge( node,each_child_child    ):
                            G_output.remove_bi_edge(  node,each_child_child    )

        return G_output







    def _Remove_rev_Singleton(  G   ):
        '''将所有的反向singleton删除，这样得到的图比较好看'''
        singleton_deleted = []
        for node in G:
            if  not G.successors(node) and not G.predecessors(  node  ):
                if node.endswith('-'):
                    singleton_deleted.append( node )
        G.remove_nodes_from( singleton_deleted  )	







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

    G_Trimed = _Trim_node( G_contig_init )


    #双向图变成单向图
    ##首先，将singleton的反向节点删除
    _Remove_rev_Singleton(G_Trimed)

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


class  Contig_Graph(nx.DiGraph):
    def __init__(self, data=None, **attr):
        super(Contig_Graph,self).__init__(data,**attr)
        self.new_id = 0
        self.assembly_detail = {}
    @staticmethod
    def reverse(data):
        #转换成为反向节点
        return [x.translate(libary) for x in data[::-1] ]

    def add_bi_edge(self,start,end):

        super(Contig_Graph,self).add_edge(start,end)
        start,end = self.reverse( [start,end] )

        super(Contig_Graph,self).add_edge(start,end)
    def remove_bi_edge(self,start,end):
        if self.has_edge(start,end):
            super(Contig_Graph,self).remove_edge(start,end)
        start,end = self.reverse([start,end])
        if self.has_edge(start,end): 
            super(Contig_Graph,self).remove_edge(start,end)
    def remove_bi_edges_from(self,edges_list  ):
        for key in edges_list:
            self.remove_bi_edge(key)

    def add_bi_edges_from(self,edges_list   ):
        for key in edges_list:
            self.add_bi_edge(key)

    def remove_bi_path(self,paths):
        for i  in xrange(1,len(paths)):
            if self.has_edge(paths[i-1],paths[i]):
                self.remove_bi_edge(paths[i-1],paths[i])
    def add_bi_path(self,paths):
        for i  in xrange(1,len(paths)):
            if paths[i] not in self.node:
                self.add_node(paths[i],name = paths[i])
                self.add_node(paths[i].translate(libary),name = paths[i].translate(libary))
            self.add_bi_edge(paths[i-1],paths[i])	
    def remove_bi_node( self,node  ):
        if not node.endswith('+') and not node.endswith("-"):
            node = node+'+'
        self.remove_nodes_from( [node, node.translate(libary)]   ) 
    def has_repeat_path(self,start,end,unique_contig):
        assert start[:-1] in unique_contig
        assert end[:-1] in unique_contig
        if start not in self.node or end not in self.node:
            return None
        No_Other_Graph = deepcopy(self) 

        for each_key in unique_contig:
            if each_key not in [ start[:-1],end[:-1]  ]:
                No_Other_Graph.remove_bi_node(each_key)
        if start.translate(libary) in self.node:
            No_Other_Graph.remove_node(start.translate(libary))
        if end.translate(libary) in self.node:
            No_Other_Graph.remove_node(end.translate(libary))

        if nx.algorithms.has_path(No_Other_Graph, start, end):
            end_path_list = []
            for path in nx.algorithms.all_simple_paths(No_Other_Graph,start,end):
                end_path_list.append(path)
            return end_path_list
        else:
            return None
    def check_path(self,start,end ,unique_contig ):
        candidate_path = self.has_repeat_path(start, end, unique_contig)
        if candidate_path:
            if len(candidate_path)==1:
                candidate_path = candidate_path[0]
                all_children= self.successors(start)
                for each_child in all_children:

                    self.remove_bi_edge(start,each_child)


                all_parents = self.predecessors(end)		
                for each_parent in all_parents:

                    self.remove_bi_edge(each_parent,end)				

                if len(candidate_path)>2:
                    candidate_path = candidate_path[1:-1]

                    if "; ".join(candidate_path) not in self.assembly_detail:
                        name = "New%s"%(self.new_id)
                        self.assembly_detail["; ".join(candidate_path)] = [name+'+',1]
                        self.assembly_detail['; '.join(self.reverse(candidate_path))] = [name+'-',1]
                        self.new_id+=1

                        MAPPING.write(
                            "%s\t%s\tDoubt\n"%(name,'; '.join(candidate_path)  
                                        )  
                        )
                        new_name = name+'+_1'
                        self.add_node(new_name,name =new_name   )
                        rev_name = new_name.translate(libary)
                        self.add_node(rev_name, name =rev_name )
                    else:
                        self.assembly_detail["; ".join(candidate_path)][1]+=1
                        self.assembly_detail['; '.join(self.reverse(candidate_path))][1]+=1
                        new_name = self.assembly_detail['; '.join(candidate_path)][0] + "_"+str(self.assembly_detail['; '.join(candidate_path)][1] )
                        rev_name = new_name.translate(libary)
                        self.add_node(new_name,name =  new_name  )
                        self.add_node(rev_name,name =  rev_name  )

                    self.add_bi_path([start,new_name,end])
                else:
                    self.add_bi_edge(start, end)
            else:
                print(candidate_path)

def Coverage_count(COVERAGE):
    all_coverage = []
    for t,s  in fasta_check( COVERAGE  ):
        cov_list = [int (x) for x in s.split()]
        all_coverage.extend(cov_list)

    cov_median = np.median(all_coverage)
    stand = np.std(all_coverage)

    output_cov = cov_median*1.5
    return output_cov



def Get_Contig( G  ):

    """获得contig，并且将一些单链和成环的contig删除"""
    #G_Trimed输出被检查过的结果
    #has_checked输出不需要检查的节点（已经是其他contig的子路径，或者该路径已经被查询完毕）
    #deleted_node输出冗余和检查过的双向图结果，即正向已经被证明是singleton或者plasmid，反向直接扔掉
    #另外，deleted_node还记录已经被检查完，放入contig的reads，在最后的图中，统一删除
    #Contig_relation 记录每一个contig的连接关系



    has_checked = {}
    deleted_node = {}
    plasmid_contig = {}
    Contig_relation = {}
    #DETAIL记录Contig的明细信息

      
    DETAIL.write("Contig\tDetail\tCategory\n")   
    #这是个计数器，用来最后contig1的编号 


    def __Enlongation_5(node):
        #查询overlap图，向5’端延伸，删除成环的节点
        
        if node in has_checked:
            return 1
        already_in_path[ node ] = ''
        has_checked[ node ] = ''

        if len(  G.predecessors(node)  ) < 2:
            predecessor  = G.predecessors(node)
            if predecessor:
                predecessor = predecessor[0]
                if  len( G.successors( predecessor ) )==1:
                    if predecessor not in already_in_path:
                        already_in_path[ predecessor  ] = ''
                        path.insert( 0 ,predecessor)
                        __Enlongation_5( predecessor)
                    else:
                        status =  2
                        return status

                else:
                    status = 1
                    return status


        else:
            status =1
            return status
    def __Enlongation_3(node):
        #查询overlap图，删除成环的节点

        has_checked[node] = ''

        if len(G.successors(node))<2:

            successor  = G.successors(node)

            if successor:
                successor = successor[0]

                if successor in has_checked:
                    status = 1
                    return status

                if  len( G.predecessors( successor ) )==1:

                    already_in_path[ successor  ] = ''
                    path.append( successor)
                    __Enlongation_3( successor)

                else:
                    status = 1
                    return status
        else:
            status =1	
            return status


    def __Check_result():
        def ___Trans_data(pa, na):
            """用于迁移连接关系"""
            start_node =  pa[0]
            end_node =  pa[-1]
            for each_succ in G_Output.successors(end_node):

                G_Output.add_edge(na, each_succ)

            for each_pred in G_Output.predecessors(start_node) :
                G_Output.add_edge(each_pred, na)

        """检查最后的path结果"""
        global Assembled_Contig_no
        new_contig_name =  "%s%s" % ( name_prefix,  Assembled_Contig_no )

        Assembled_Contig_no+= 1
        #迁移连接关系
        #如果status==1，则该contig两边都连接不确定的关系，该contig的正反向都保留
        #如果status==2，则该contig直接就是一个质粒，所有的正向、反向节点都删除，
        #如果status==0，则该contig为一个链状contig，删除反向节点，不做关系迁移
        #所有的相关节点都准备删掉
        Contig_relation[new_contig_name] = path
        for d_node in path:
            traversed_node =  d_node.translate(libary)
            deleted_node[ traversed_node ]  = ''
            deleted_node[ d_node ]  = ''
            has_checked[ traversed_node ]  = ''
        ##链状和环状contig去除
        if status != 1:
            #删除节点
            G_Output.add_node(new_contig_name+'+', name = new_contig_name+'+')

            if status == 0:
                category = "Chain"
            else:
                category =  "Plasmid"
                plasmid_contig[new_contig_name]  =  path
                G_Output.add_edge(new_contig_name+'+',  new_contig_name+'+') 
            DETAIL.write (new_contig_name+'\t'+'; '.join(path)+"\t"+category+'\n'  )

        else:

            category =  "Doubt"
            #正向节点迁移
            DETAIL.write (new_contig_name+'\t'+'; '.join(path)+"\t"+category+'\n'  )
            G_Output.add_node(new_contig_name+'+', name = new_contig_name+'+' )
            ___Trans_data(path,new_contig_name+'+' )
            #反向节点迁移
            G_Output.add_node(new_contig_name+'-', name = new_contig_name+'-' )
            rev_path = [ i.translate(libary)  for i in   path[::-1] ]
            ___Trans_data(rev_path,new_contig_name+'-' )





    for each_node in G:
        if each_node  in deleted_node:
            continue
        #path用来计路径，already_in_path用来记录那些节点已经出现在路径中
        #status用来记录是否需要将该路径对应的反向节点删除
        path = [each_node]
        status = 0

        #status 可以为三种情况，0的话是singlton节点，1的时候是开叉分支，2的时候是plasmid节点
        already_in_path = {}

        end  = __Enlongation_5(each_node)

        if end is not None:
            status =end
        end = __Enlongation_3(each_node)
        if end ==1:
            status = 1            
        __Check_result()
    for each_node in deleted_node:

        if each_node in G_Output.node:
            G_Output.remove_node(each_node)
    return  Contig_relation, plasmid_contig,G_Output



































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
    G_Output =  deepcopy(G_Contig)
    DETAIL =  open(name_prefix+'.assembly_detail', 'w') 
    Contig_relation,plasmid_contig ,G_Output = Get_Contig(G_Contig)
    Final_assembly_commandline =shlex.split( "./Post_assembly.py -u %s -r %s -o Reference_Final"%(NEW_CONTIG_REF_ADD.name, DETAIL.name ) )
    
    subprocess.check_output(Final_assembly_commandline)    