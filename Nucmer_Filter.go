// Nucmer_Filter
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
	file_handle.Next()
	for {
		line, err := file_handle.Next()
		data_all := bytes.Fields(bytes.TrimSpace(line))

		if len(data_all) < 3 {
			break
		}
		query := string(data_all[len(data_all)-2])
		subject := string(data_all[len(data_all)-3])

		query_length := Conver(data_all[8])
		subj_length := Conver(data_all[7])
		if string(data_all[len(data_all)-1]) == "[IDENTITY]" {
			if query_length > subj_length {
				all_filtered[subject] = ""
			} else if query_length < subj_length {
				all_filtered[query] = ""
			}
		} else if string(data_all[11]) == "[CONTAINS]" {
			all_filtered[query] = ""

		} else if string(data_all[len(data_all)-1]) == "[CONTAINED]" {
			all_filtered[subject] = ""
		}
		if err != nil {
			break
		}
	}
	file_handle2, _ := GetBlockRead(*input, "\n", false, 100000000)
	file_handle2.Next()
	for {
		line, err := file_handle2.Next()
		data_all := bytes.Fields(bytes.TrimSpace(line))
		if len(data_all) < 3 {
			break
		}

		query := string(data_all[len(data_all)-2])
		subject := string(data_all[len(data_all)-3])
		if query == subject {
			continue
		}
		if _, has1 := all_filtered[query]; has1 {
			continue

		} else if _, has2 := all_filtered[subject]; has2 {
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
