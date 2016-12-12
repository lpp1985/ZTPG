// DAFILTER
package main

import (
	"bufio"
	"bytes"
	"flag"
	"strconv"
	//	"fmt"
	. "lpp"
	"os"
)

func Conver(input []byte) int {
	number, _ := strconv.Atoi(string(input))
	return number
}
func main() {

	output := flag.String("o", "output", "output")
	input := flag.String("i", "input", "input")
	exclude := flag.String("e", "exclude_list", "exclude list!")

	flag.Parse()
	result, _ := os.Create(*output)
	exclude_file, _ := os.Create(*exclude)
	defer result.Close()
	new_output := bufio.NewWriter(result)
	defer new_output.Flush()
	exclude_output := bufio.NewWriter(exclude_file)
	defer exclude_output.Flush()
	file_handle, _ := GetBlockRead(*input, "\n", false, 1000000)
	all_filtered := make(map[string]string)
	for {
		line, err := file_handle.Next()
		data_all := bytes.Fields(bytes.TrimSpace(line))

		if len(data_all) < 3 {
			break
		}
		query := string(data_all[0])
		subject := string(data_all[1])
		query_start := Conver(data_all[5])
		query_end := Conver(data_all[6])
		query_length := Conver(data_all[7])
		subj_start := Conver(data_all[9])
		subj_end := Conver(data_all[10])
		subj_length := Conver(data_all[11])
		if string(data_all[len(data_all)-1]) == "contains" {
			all_filtered[string(data_all[1])] = ""

		} else if string(data_all[len(data_all)-1]) == "contained" {
			all_filtered[string(data_all[0])] = ""
		} else if query_end-query_start == query_length {
			all_filtered[query] = ""
		} else if subj_end-subj_start == subj_length {
			all_filtered[subject] = ""
		}
		if err != nil {
			break
		}
	}
	file_handle2, _ := GetBlockRead(*input, "\n", false, 1000000)
	for {
		line, err := file_handle2.Next()
		data_all := bytes.Fields(bytes.TrimSpace(line))
		if len(data_all) < 3 {
			break
		}
		if _, has1 := all_filtered[string(data_all[0])]; has1 {
			continue

		} else if _, has2 := all_filtered[string(data_all[1])]; has2 {
			continue
		}
		new_output.Write(line)
		if err != nil {
			break
		}
	}
	for key, _ := range all_filtered {
		exclude_output.WriteString(key + "\n")
	}

}
