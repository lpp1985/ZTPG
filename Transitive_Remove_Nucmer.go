package main

import (
	//	"bufio"
	"bytes"
	"flag"

	. "lpp"
	"os"
	"sort"
	"strconv"
	"strings"
)

func Max(input []int) int {
	sort.Sort(sort.Reverse(sort.IntSlice(input)))
	return input[0]

}

type Align_Graph struct {
	Graph_hash map[string]map[string]int
	All_nodes  map[string]string
}

func (Graph *Align_Graph) Init() {
	Graph.Graph_hash = make(map[string]map[string]int)
	Graph.All_nodes = make(map[string]string)
}
func TransitiveRemove(Graph map[string]map[string]int) map[string]map[string]string {

	mark := make(map[string]string)
	reduce := make(map[string]map[string]string)
	//Transfer to false and valcant
	for each_node := range Graph {
		mark[each_node] = "vacant"
	}

	for each_node, succ_hash := range Graph {

		align_length_list := []int{}
		align_length_hash := make(map[int]map[string]string)
		for each_succ := range succ_hash {
			mark[each_succ] = "Inplay"

			fuzz_length := Graph[each_node][each_succ]
			align_length_list = append(align_length_list, fuzz_length)
			_, alnlengthok := align_length_hash[fuzz_length]
			if !alnlengthok {
				align_length_hash[fuzz_length] = make(map[string]string)
			}
			align_length_hash[fuzz_length][each_succ] = ""
		}
		if len(align_length_list) < 1 {
			continue
		} else {
			sort.Sort(sort.Reverse(sort.IntSlice(align_length_list)))

		}

		for _, vol1_length := range align_length_list {
			for succ_node := range align_length_hash[vol1_length] {
				if mark[succ_node] == "Inplay" {

					align2_length_list := []int{}
					align2_length_hash := make(map[int]map[string]string)

					for each_succ_succ := range Graph[succ_node] {

						fuzz2_length := Graph[succ_node][each_succ_succ]
						align2_length_list = append(align2_length_list, fuzz2_length)
						_, succ2_ok := align2_length_hash[fuzz2_length]
						if !succ2_ok {
							align2_length_hash[fuzz2_length] = make(map[string]string)

						}
						align2_length_hash[fuzz2_length][each_succ_succ] = ""

					}

					sort.Sort(sort.Reverse(sort.IntSlice(align2_length_list)))
					for _, each_fuzz2Length := range align2_length_list {
						for succ_succ_node := range align2_length_hash[each_fuzz2Length] {

							if mark[succ_succ_node] == "Inplay" {
								mark[succ_succ_node] = "eliminated"
							}

						}

					}

				}
			}

		}

		for each_succ, _ := range succ_hash {
			if mark[each_succ] == "eliminated" {
				_, red_ok := reduce[each_node]
				if !red_ok {
					reduce[each_node] = make(map[string]string)
				}
				reduce[each_node][each_succ] = ""
			}
			mark[each_succ] = "vacant"
		}
	}
	//	fmt.Println(reduce)
	return reduce
}

func (Graph *Align_Graph) AddEdges(start string, end string, length int) {

	start_node := start[:len(start)-1] + "+"
	end_node := end[:len(end)-1] + "+"
	Graph.All_nodes[start_node] = ""
	Graph.All_nodes[end_node] = ""
	_, ok := Graph.Graph_hash[start]
	if !ok {
		Graph.Graph_hash[start] = make(map[string]int)
		Graph.Graph_hash[start][end] = length

	} else {
		Graph.Graph_hash[start][end] = length

	}

	start_new := end[:len(end)-1]
	end_new := start[:len(start)-1]
	if strings.HasSuffix(end, "-") {
		start_new = start_new + "+"
	} else {
		start_new = start_new + "-"
	}
	if strings.HasSuffix(start, "-") {
		end_new = end_new + "+"
	} else {
		end_new = end_new + "-"
	}
	_, ok2 := Graph.Graph_hash[start_new]
	if !ok2 {
		Graph.Graph_hash[start_new] = make(map[string]int)
		Graph.Graph_hash[start_new][end_new] = length

	} else {
		Graph.Graph_hash[start_new][end_new] = length

	}
}

func (Graph *Align_Graph) DelEdges(start_node string, end_node string) {

	delete(Graph.Graph_hash[start_node], end_node)

	start_new := end_node
	end_new := start_node
	if strings.HasSuffix(start_new, "-") {
		start_new = start_new[:len(start_new)-1] + "+"

	} else {
		start_new = start_new[:len(start_new)-1] + "-"
	}

	if strings.HasSuffix(end_new, "-") {
		end_new = end_new[:len(end_new)-1] + "+"

	} else {
		end_new = end_new[:len(end_new)-1] + "-"
	}
	delete(Graph.Graph_hash[start_new], end_new)

}

func Conver(input []byte) int {
	number, _ := strconv.Atoi(string(input))

	return number

}
func main() {
	ovl := flag.String("o", "output", "output")
	input := flag.String("i", "input", "input")
	overlap_length := flag.Int("l", 1000, "overlap length")
	graph := flag.String("g", "overlap.graph", "overlap graph")
	flag.Parse()
	OVL, _ := os.Create(*ovl)
	defer OVL.Close()
	string_graph := Align_Graph{}
	string_graph.Init()
	overlap_data, _ := GetBlockRead(*input, "\n", false, 100000)

	for {
		line, err := overlap_data.Next()
		if len(line) < 2 {
			break
		}
		data_all := bytes.Fields(bytes.TrimSpace(line))
		query := string(data_all[len(data_all)-2])
		subject := string(data_all[len(data_all)-3]) + "+"

		align_length := Conver(data_all[4])
		query_start := Conver(data_all[2]) - 1
		query_end := Conver(data_all[3]) - 1
		if align_length < *overlap_length {
			continue
		}
		align_ord := "+"
		if query_start > query_end {
			align_ord = "-"

		}
		query = query + align_ord
		if string(data_all[11]) == "[BEGIN]" {
			string_graph.AddEdges(query, subject, align_length)
		} else if string(data_all[11]) == "[END]" {
			string_graph.AddEdges(subject, query, align_length)
		}
		if err != nil {
			break
		}

	}
	del_edge_hash := TransitiveRemove(string_graph.Graph_hash)

	for key1, succ_hash := range del_edge_hash {
		for key2 := range succ_hash {
			string_graph.DelEdges(key1, key2)

		}

	}
	OVL_DATA, _ := GetBlockRead(*input, "\n", false, 100000)
	for {

		line, err := OVL_DATA.Next()
		if len(line) < 2 {
			break
		}

		data_all := bytes.Fields(bytes.TrimSpace(line))
		query := string(data_all[len(data_all)-2])
		subject := string(data_all[len(data_all)-3]) + "+"

		align_length := Conver(data_all[4])
		query_start := Conver(data_all[2]) - 1
		query_end := Conver(data_all[3]) - 1
		if align_length < *overlap_length {
			continue
		}
		align_ord := "+"
		if query_start > query_end {
			align_ord = "-"

		}
		query = query + align_ord
		if string(data_all[11]) == "[BEGIN]" {
			_, new_ok := string_graph.Graph_hash[query][subject]
			if new_ok {
				OVL.Write(line)
			}
		} else if string(data_all[11]) == "[END]" {

			_, new_ok := string_graph.Graph_hash[subject][query]
			if new_ok {
				OVL.Write(line)

			}
		}

		if err != nil {
			break
		}

	}
	GRAPH, _ := os.Create(*graph + ".edges")
	defer GRAPH.Close()
	NODE, _ := os.Create(*graph + ".nodes")
	for source, succ_hash := range string_graph.Graph_hash {
		for succ := range succ_hash {
			GRAPH.WriteString(string(source) + "\t" + string(succ) + "\n")

		}
	}
	for each_node := range string_graph.All_nodes {
		NODE.WriteString(string(each_node) + "\n")
	}
	//Start to Remove Transitive Edges

}
