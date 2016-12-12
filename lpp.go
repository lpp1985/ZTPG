// lpp
package lpp

import (
	"bufio"
	"bytes"
	//	"fmt"
	"io"
	"os"
	"sort"
)

func RevComplement(char []byte) []byte {
	var complement = [256]uint8{
		'A': 'T', 'a': 'T',
		'C': 'G', 'c': 'G',
		'G': 'C', 'g': 'C',
		'T': 'A', 't': 'A',
		'U': 'A', 'u': 'A',
		'M': 'K', 'm': 'K',
		'R': 'Y', 'r': 'Y',
		'W': 'W', 'w': 'W',
		'S': 'S', 's': 'S',
		'Y': 'R', 'y': 'R',
		'K': 'M', 'k': 'M',
		'V': 'B', 'v': 'B',
		'H': 'D', 'h': 'D',
		'D': 'H', 'd': 'H',
		'B': 'V', 'b': 'V',
		'N': 'N', 'n': 'N',
	}
	L := len(char)
	new_base := make([]byte, L)

	for _, base := range char {
		L--
		new_base[L] = complement[base]

	}
	return new_base
}

type File_Ddict struct {
	File_IO IO
	Header  bool
}

func (file *File_Ddict) Read(key int, value int) map[string]map[string]string {
	key--
	value--
	var result_hash map[string]map[string]string = make(map[string]map[string]string)
	if file.Header == true {
		file.File_IO.Next()
	}

	for {

		line, err := file.File_IO.Next()
		if err != nil {
			break
		}
		line_l := bytes.Split(bytes.TrimSpace(line), []byte("\t"))

		if len(line_l) > sort.IntSlice([]int{key, value})[0] {
			key_string := string(line_l[key])
			value_string := string(line_l[value])
			_, ok := result_hash[key_string][value_string]

			if !ok {
				result_hash[key_string] = make(map[string]string)
				result_hash[key_string][value_string] = ""

			}
		}

	}
	return result_hash
}

type File_dict struct {
	File_IO IO
	Header  bool
}

func (file *File_dict) Read(key int, value int) map[string]string {
	key--
	value--
	var result_hash map[string]string = make(map[string]string)

	if file.Header == true {
		file.File_IO.Next()
	}
	for {

		line, err := file.File_IO.Next()
		if err != nil {
			break
		}
		line_l := bytes.Split(bytes.TrimSpace(line), []byte("\t"))
		if len(line_l) > sort.IntSlice([]int{key, value})[0] {
			key_string := string(line_l[key])
			value_string := string(line_l[value])
			result_hash[key_string] = value_string

		}

	}
	return result_hash
}

type Block_Reading struct {
	File     string
	Blocktag string
	Buffer   int
}
type IO struct {
	Io       *bufio.Reader
	BlockTag []byte
	SplitTag byte
}

func (blockreading *Block_Reading) Read() (IO, error) {
	BlockIO := IO{}

	raw_file, err := os.Open(blockreading.File)
	if blockreading.Buffer == 0 {
		blockreading.Buffer = 99999999
	}
	BlockIO.Io = bufio.NewReaderSize(raw_file, blockreading.Buffer)
	if blockreading.Blocktag == "" {
		BlockIO.BlockTag = []byte("\n")
	} else {
		BlockIO.BlockTag = []byte(blockreading.Blocktag)
	}
	BlockIO.SplitTag = byte([]byte(blockreading.Blocktag)[len(blockreading.Blocktag)-1])

	return BlockIO, err

}
func GetBlockRead(name string, blocktag string, header bool, buffer int) (IO, error) {
	BR := new(Block_Reading)
	BR.Blocktag = blocktag
	BR.Buffer = buffer
	BR.File = name
	Result_IO, err := BR.Read()
	if err != nil {
		return Result_IO, err
	}
	if header {
		Result_IO.Next()
	}
	return Result_IO, err
}
func (Reader IO) Next() ([]byte, error) {

	var out_tag []byte
	var status error

	for {
		line, err := Reader.Io.ReadSlice(Reader.SplitTag)

		if err == nil {
			if len(out_tag) > 1 {
				out_tag = append(out_tag, line...)
			} else {
				out_tag = line
			}

			if len(Reader.BlockTag) > 1 {
				if len(out_tag) >= len(Reader.BlockTag) && bytes.Equal(out_tag[(len(out_tag)-len(Reader.BlockTag)):], Reader.BlockTag) {

					break
				}

			} else {
				break
			}

		} else if err == bufio.ErrBufferFull || err == io.EOF {
			if err == io.EOF {
				status = err
				out_tag = append(out_tag, line...)
				break
			}
			out_tag = append(out_tag, line...)

		}

	}

	return out_tag, status

}
