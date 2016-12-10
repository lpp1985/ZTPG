// Change_Illumina
package main

import (
	"bufio"
	"bytes"
	"flag"
	"fmt"
	"lpp"
	"os"
	"regexp"
)

func main() {
	output := flag.String("o", "output", "output")
	input := flag.String("i", "input", "input")
	name := flag.String("f", "reads", "reads")
	reads := flag.String("r", "all_reads.fasta", "reads")
	flag.Parse()
	result, _ := os.Create(*output)
	defer result.Close()
	all_result, _ := os.Create(*reads)
	all_output := bufio.NewWriter(all_result)
	defer all_output.Flush()
	new_output := bufio.NewWriter(result)
	raw_handle := new(lpp.Block_Reading)

	raw_handle.File = *input
	raw_handle.Blocktag = ">"
	file_handle, _ := raw_handle.Read()
	i := 0
	file_handle.Next()
	for {
		line, err := file_handle.Next()
		line = bytes.TrimSuffix(line, []byte(">"))

		seq := bytes.SplitN(line, []byte("\n"), 2)[1]
		seq2 := bytes.Replace(seq, []byte("\n"), []byte(""), -1)
		seq2_regex := regexp.MustCompile("N+")
		seq_string_list := seq2_regex.Split(string(seq2), -1)
		if len(seq_string_list) != 1 {

			for _, strseq := range seq_string_list {
				name := fmt.Sprintf(">%s/%d/0_%d\n", name, i, len(strseq))
				new_output.WriteString(name + strseq + "\n")
				name2 := fmt.Sprintf(">%d\n", i)
				all_output.WriteString(name2 + strseq + "\n")
				i++

			}
		} else {

			name := []byte(fmt.Sprintf(">%s/%d/0_%d\n", *name, i, len(seq2)))

			end_seq := append(name, seq...)
			new_output.Write(end_seq)
			name2 := []byte(fmt.Sprintf(">%d\n", i))
			end_seq = append(name2, seq...)
			all_output.Write(end_seq)
			i++
		}

		if err != nil {
			break
		}
	}
	new_output.Flush()
}
