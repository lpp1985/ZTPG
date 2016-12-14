// Generate_Unitig
package main

import (
	"bufio"
	"bytes"
	"flag"
	"fmt"
	. "lpp"
	"os"
	"regexp"
	"strconv"
)

func ConverInt(char []byte) int {

	result, _ := strconv.Atoi(string(char))
	return result

}
func main() {
	space_regex := regexp.MustCompile("\\s+")
	ovl := flag.String("i", "OVL.Graph", "Overlap")
	read := flag.String("f", "Reads.fasta", " All Reads fasta format")
	unitig := flag.String("o", "All_Unitig.fasta", "unitig output")

	flag.Parse()
	untig_handle, _ := os.Create(*unitig)
	defer untig_handle.Close()
	UNITIG := bufio.NewWriter(untig_handle)
	defer UNITIG.Flush()
	FASTA, _ := GetBlockRead(*read, "\n>", false, 100000)

	all_reads := make(map[string]string)
	i := 0
	for {
		line, err := FASTA.Next()
		if i == 0 {
			line = line[1:]
			i++
		}
		line_l := bytes.SplitAfterN(line, []byte("\n"), 2)
		title := string(bytes.Fields(line_l[0])[0])

		seq := space_regex.ReplaceAll(line_l[1], []byte(""))
		seq = bytes.TrimSuffix(seq, []byte(">"))
		all_reads[title+"+"] = string(seq)
		fmt.Println(title+"+", len(seq))
		all_reads[title+"-"] = string(RevComplement(seq))

		if err != nil {
			break
		}

	}

	OVL, _ := GetBlockRead(*ovl, "\n", false, 1000000)
	for {
		unitig_seq := ""
		line, err := OVL.Next()

		if len(line) < 2 {
			break
		}
		line_l := bytes.Fields(line)
		query := string(line_l[10])
		subj := string(line_l[9])
		query_end := ConverInt(line_l[3]) - 1
		query_start := ConverInt(line_l[2]) - 1
		subj_start := ConverInt(line_l[0]) - 1
		subj_end := ConverInt(line_l[1]) - 1
		fmt.Println(subj_start, subj_end)
		align_ord := "+"
		if query_start > query_end {
			align_ord = "-"
			query_start, query_end = query_end, query_start
		}
		if string(line_l[11]) == "[END]" {
			if align_ord == "+" {
				UNITIG.WriteString(">" + subj + "+" + "__" + query + "+" + "\n")
				unitig_seq = all_reads[query+"+"][query_end:]

				UNITIG.WriteString(unitig_seq + "\n")
				UNITIG.WriteString(">" + query + "-" + "__" + subj + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[subj+"+"][:subj_start])))
				UNITIG.WriteString(unitig_seq + "\n")
			} else {
				UNITIG.WriteString(">" + subj + "+" + "__" + query + "-" + "\n")

				unitig_seq = string(RevComplement([]byte(all_reads[query+"+"][:query_start])))
				UNITIG.WriteString(unitig_seq + "\n")
				UNITIG.WriteString(">" + query + "+" + "__" + subj + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[subj+"+"][:subj_start])))
				UNITIG.WriteString(unitig_seq + "\n")

			}
		} else if string(line_l[11]) == "[BEGIN]" {
			if align_ord == "+" {
				UNITIG.WriteString(">" + query + "+" + "__" + subj + "+" + "\n")
				unitig_seq = all_reads[subj+"+"][subj_end:]
				UNITIG.WriteString(unitig_seq + "\n")
				UNITIG.WriteString(">" + subj + "-" + "__" + query + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[query+"+"][:query_start])))
				UNITIG.WriteString(unitig_seq + "\n")

			} else {

				UNITIG.WriteString(">" + query + "-" + "__" + subj + "+" + "\n")
				unitig_seq = all_reads[subj+"+"][subj_end:]
				UNITIG.WriteString(unitig_seq + "\n")
				UNITIG.WriteString(">" + subj + "+" + "__" + query + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[query+"+"][query_end:])))
				UNITIG.WriteString(unitig_seq + "\n")

			}

		}

		if err != nil {
			break
		}

	}

}
