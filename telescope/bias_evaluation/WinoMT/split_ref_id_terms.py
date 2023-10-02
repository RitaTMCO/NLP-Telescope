from typing import List
import argparse
    
def read_file(filename:str):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    return lines


def write_file(ref_filename:str, id_filename:str, data:List[str]):
    f_ref = open( ref_filename, "w")
    f_id = open( id_filename, "w")

    lines = [i for i in range(len(data))]

    for line in lines:
        data_line = data[line]
        b = 0
        e = 0
        e_ref = 0
        for c in range(len(data_line)):
            if data_line[c] == "[" and b == 0:
                b = c
            if data_line[c] == "]" and e == 0:
                e = c
            if data_line[c] == "." and e_ref == 0:
                e_ref = c
        if data_line != data[lines[-1]]:
            f_ref.write(data_line[0:e_ref+1] + "\n")
            f_id.write(data_line[b:e+1] + "\n")
        else:
            f_ref.write(data_line[0:e_ref+1])
            f_id.write(data_line[b:e+1])
    f_ref.close()
    f_id.close() 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="Input path",
        required=True,
        type=str
    )
    parser.add_argument(
        "-t",
        "--id_terms_name",
        help="Identity terms filename.",
        required=True,
        type=str
    )
    parser.add_argument(
        "-r",
        "--reference",
        help="Reference filename.",
        required=True,
        type=str
    )

    args = parser.parse_args()
    data = read_file(args.input)
    write_file(args.reference, args.id_terms_name, data)

