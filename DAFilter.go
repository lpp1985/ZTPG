// DAFILTER
package main

import (
	"bufio"
	"bytes"
	"flag"
	//	"fmt"
	. "lpp"
	"os"
)

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
		if string(data_all[len(data_all)-1]) == "contains" {
			all_filtered[string(data_all[1])] = ""

		} else if string(data_all[len(data_all)-1]) == "contained" {
			all_filtered[string(data_all[0])] = ""
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
