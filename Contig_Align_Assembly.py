#!/usr/bin/env python
#coding:utf-8
# Author:   --<>
# Purpose: 
# Created: 2014/4/9


from copy import deepcopy
import subprocess
from lpp import *
from  jinja2 import FileSystemLoader,Environment
import json
from Dependency import *
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
    #os.system(  "nucmer --maxmatch %(genome)s  %(genome)s -p cache"%( {"genome":file_name }  )  )
    align_data = os.popen(  """show-coords  cache.delta -odTl   | grep -P  "\[\S+\]$" """      )
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










    #首先对所有的reads做筛选，将contain和完全相同的去除掉
    deleted_node = {}
    #检查contain关系，并将所有contain的节点删除
    CONTAIN = open( name_prefix+'.contains','w'  )
    containeed_line = {}
    CONTAIN.write( "Contig\tIncluded_by\n"  )
    for each_line in output_category[ "CONTAINS"  ]:
        line_l = each_line.strip().split("\t")
        big_contig,small_contig = Get_list( line_l,[11,12] )
        deleted_node[ small_contig ] = ''
        containeed_line[  small_contig+'\t'+big_contig+'\n' ] = ''
        #CONTAIN.write( small_contig+'\t'+big_contig+'\n'   )
    #检查contained关系
    for each_line in output_category[ "CONTAINED"  ]:
        line_l = each_line.strip().split("\t")
        big_contig,small_contig = Get_list( line_l,[12,11] )
        deleted_node[ small_contig ] = ''
        containeed_line[ small_contig+'\t'+big_contig+'\n'    ] = ''
        #CONTAIN.write( small_contig+'\t'+big_contig+'\n'   )
    for data in containeed_line:
        CONTAIN.write(data)
    #检查identity
    for each_line in output_category[ "IDENTITY"  ]:
        line_l = each_line.strip().split("\t")
        query_length,subject_length,query_contig,subject_contig = Get_list( line_l,[7,8,11,12] )
        query_length =int( query_length );subject_length = int( subject_length )
        if query_length>subject_contig:
            small_contig = subject_contig
            big_contig = query_contig
        else:
            small_contig = query_contig
            big_contig = subject_contig
        deleted_node[ small_contig ] = ''
        CONTAIN.write( small_contig+'\t'+big_contig+'\n'   )		

    #开始对 Start和END进行解析，期间只要碰到 删除的节点，就跳过
    #设置一个初始图
    Overlap_Graph = Contig_Graph()
    # 添加所有的节点 添加双向
    FASTA = fasta_check(open( file_name ,'rU') )
    for t,s in FASTA:
        each_contig = t.strip().split()[0][1:]
        if each_contig not in deleted_node:
            each_contig= each_contig+"+"
            Overlap_Graph.add_bi_node(each_contig)

    #根据Begin和END添加关系
    #根据BEGIN进行构图

    for each_line in output_category[ "BEGIN"  ]:
        line_l = each_line.split("\t")
        query_node,subj_node,frame = Get_list( line_l,[ 11,12,10 ]  )
        #如果删除的节点出现了这些数据则跳过
        if query_node in deleted_node or subj_node in deleted_node:
            continue

        #否则
        if frame =="1":
            direction = "+"
        else:
            direction = '-'

        Overlap_Graph.add_bi_edge(  subj_node+direction, query_node+'+'    )



    #根据END进行构图
    for each_line in output_category[ "END"  ]:
        line_l = each_line.split("\t")
        query_node,subj_node,frame = Get_list( line_l,[ 11,12,10 ]  )
        #如果删除的节点出现了这些数据则跳过
        if query_node in deleted_node or subj_node in deleted_node:
            continue

        #否则
        if frame =="1":
            direction = "+"
        else:
            direction = '-'

        Overlap_Graph.add_bi_edge( query_node+'+', subj_node+direction    )



    #修图，将tiling边删除
    G_Trimed = Transitive_Remove( Overlap_Graph )
    Draw_Web("see.html", Overlap_Graph)

    #双向图变成单向图
    ##首先，将singleton的反向节点删除
    Remove_rev_Singleton(G_Trimed)
    


    DETAIL = open( name_prefix+'.contains','w'  )
    Contig_relation,plasmid_contig,G_Output = Get_Contig(G_Trimed,DETAIL,name_prefix)

    return  Contig_relation,plasmid_contig,G_Output
    ##到目前为止 G_Trimed完成，下面遍历所有的contig，遍历标准是predecessor 为1，successors为1，认为是一个contig
    ##见这些contig的明细信息保存下来



def get_para(   ):
    #获得运行参数
    usage = '''
	%prog [ options ]
	'''
    parser = OptionParser( usage = usage  )


    parser.add_option("-i", "--Input", action="store",
                      dest="input",
                      help="input contig seqeuence in fasta format!")


    parser.add_option("-p","--prefix",action= "store",
                      dest = "prefix",
                      help=" name prefix"
                      )

    parser.add_option("-o","--Ouptut",action= "store",
                      dest = "output",
                      help=" Result Suffix "
                      )


    (options, args) = parser.parse_args()
    return options,args


if __name__=='__main__':
    options,args = get_para()
    name_prefix = options.prefix
    raw_file = options.input
    output_category = Mummer_parse( raw_file  )

    Contig_relation,plasmid_contig,G_Output= Relation_parse( raw_file, output_category )
    Draw_Web("Contig_detail.html", G_Output)
    CYCLE =  open(name_prefix+'.cycle','w')
    DETAIL = open(name_prefix+'.detail','w')

    for a,b in Contig_relation.items():
        DETAIL.write(a+'\t'+'; '.join(b)+'\n')
    for  circle in  nx.algorithms.simple_cycles(G_Output):
        CYCLE.write("\t".join(circle)+'\n')