import argparse
import os

def read_file(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    return lines

def write_file(filename,lines):
    f = open(filename, "w")
    f.writelines(lines)
    f.close()

def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def write_domain_file(input_filename,domains,output_path,filetype, output_filename):
    lines = read_file(input_filename)
    for domain, number_lines in domains.items():
        write_domain_lines = [lines[i] for i in number_lines]

        path_d = output_path + domain + "/"        
        path = path_d + filetype + "/"
        create_dir(path)

        write_file(
            filename = path + "/" + output_filename + "-" + domain,
            lines = write_domain_lines)


def domain_segments(filename):
    lines = read_file(filename)
    domains = {}
    docs = []
    for number_of_line, line in enumerate(lines):
        domain, doc = line.split("\t")
        if domain not in list(domains.keys()):
            domains[domain] = [number_of_line]
        else:
            domains[domain].append(number_of_line)
        
        if doc not in docs:
            docs.append(doc)
        
    print("number of docs: " + str(len(docs)))
    print("domains: " + str(list(domains.keys())))
    return domains


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--languages_pair",
        help="Language pair (e.g. en-ru).",
        required=True,
        type=str
    )
    parser.add_argument(
        "-i",
        "--input_path",
        help="Input path",
        required=True,
        type=str
    )

    args = parser.parse_args()

    output_path = args.input_path + "/" + args.languages_pair + "/" + "domains/"
    documents =  args.input_path + "/" + args.languages_pair + "/" + "documents/" + args.languages_pair + ".docs"
    source =  args.input_path + "/" + args.languages_pair + "/" + "sources/" + args.languages_pair + ".txt"
    references =   args.input_path + "/" + args.languages_pair + "/" + "references/" 
    systems_outputs =  args.input_path + "/" + args.languages_pair + "/" + "systems-outputs/"

    create_dir(output_path)

    domains = domain_segments(documents)

    for domain in list(domains.keys()):
        create_dir(output_path + domain + "/")
        create_dir(output_path + domain + "/nlp-telescope-scores/")

    write_domain_file(
                input_filename = source, 
                domains = domains, 
                output_path = output_path, 
                filetype = "sources",
                output_filename =  args.languages_pair)

    for reference in os.listdir(references):
        write_domain_file(
                input_filename = references + reference, 
                domains = domains, 
                output_path = output_path, 
                filetype = "references",
                output_filename =  reference)
    
    for output in os.listdir(systems_outputs):
        write_domain_file(
                input_filename = systems_outputs + output, 
                domains = domains, 
                output_path = output_path, 
                filetype = "systems-outputs",
                output_filename =  output)