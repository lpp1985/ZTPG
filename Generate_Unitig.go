// Generate_Unitig
package main

import (
	"bufio"
	"bytes"
	"flag"

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
	for {
		line, err := FASTA.Next()
		line_l := bytes.SplitAfterN(line, []byte("\n"), 2)
		title := string(bytes.TrimPrefix(bytes.Fields(line_l[0])[0], []byte(">")))
		seq := space_regex.ReplaceAll(line_l[1], []byte(""))
		seq = bytes.TrimSuffix(seq, []byte(">"))
		all_reads[title+"+"] = string(seq)
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
		query := string(line_l[0])
		subj := string(line_l[1])
		query_end := ConverInt(line_l[6])
		query_start := ConverInt(line_l[5])
		subj_start := ConverInt(line_l[9])
		subj_end := ConverInt(line_l[10])
		align_ord := "+"
		if string(line_l[8]) == "1" {
			align_ord = "-"

		}
		if query_start == 0 {
			if align_ord == "+" {
				UNITIG.WriteString(">" + subj + "+" + "__" + query + "+" + "\n")
				unitig_seq = all_reads[query+"+"][query_end:]
				UNITIG.WriteString(unitig_seq + "\n")

				UNITIG.WriteString(">" + query + "-" + "__" + subj + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[subj+"+"][:subj_start])))
				UNITIG.WriteString(unitig_seq + "\n")

			} else {

				UNITIG.WriteString(">" + subj + "-" + "__" + query + "+" + "\n")
				unitig_seq = all_reads[query+"+"][query_end:]
				UNITIG.WriteString(unitig_seq + "\n")
				UNITIG.WriteString(">" + query + "-" + "__" + subj + "+" + "\n")
				unitig_seq = all_reads[subj+"+"][subj_end:]
				UNITIG.WriteString(unitig_seq + "\n")

			}
		} else {
			if align_ord == "+" {
				UNITIG.WriteString(">" + query + "+" + "__" + subj + "+" + "\n")
				unitig_seq = all_reads[subj+"+"][subj_end:]
				UNITIG.WriteString(unitig_seq + "\n")
				UNITIG.WriteString(">" + subj + "-" + "__" + query + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[query+"+"][:query_start])))
				UNITIG.WriteString(unitig_seq + "\n")

			} else {

				UNITIG.WriteString(">" + query + "+" + "__" + subj + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[subj+"+"][:subj_start])))
				UNITIG.WriteString(unitig_seq + "\n")
				UNITIG.WriteString(">" + subj + "+" + "__" + query + "-" + "\n")
				unitig_seq = string(RevComplement([]byte(all_reads[query+"+"][:query_start])))
				UNITIG.WriteString(unitig_seq + "\n")

			}

		}

		if err != nil {
			break
		}

	}

}
