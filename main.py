from functools import reduce
from pprint import pprint
from binascii import hexlify



instruction_set = {
    "ADD": 0x18, "ADDF": 0x58, "AND": 0x40, "COMP": 0x28, "COMPF": 0x88,
    "DIV": 0x24, "DIVF": 0x64, "J": 0x3C, "JEQ": 0x30, "JGT": 0x34,
    "JLT": 0x38, "JSUB": 0x48, "LDA": 0x00, "LDB": 0x68, "LDCH": 0x50,
    "LDF": 0x70, "LDL": 0x08, "LDS": 0x6C, "LDT": 0x74, "LDX": 0x04,
    "LPS": 0xD0, "MUL": 0x20, "MULF": 0x60, "OR": 0x44, "RD": 0xD8,
    "RSUB": 0x4C, "SSK": 0xEC, "STA": 0x0C, "STB": 0x78, "STCH": 0x54,
    "STF": 0x80, "STI": 0xD4, "STL": 0x14, "STS": 0x7C, "STSW": 0xE8,
    "STT": 0x84, "STX": 0x10, "SUB": 0x1C, "SUBF": 0x5C, "TD": 0xE0,
    "TIX": 0x2C, "WD": 0xDC
}

pseudo_list = ["START", "END", "BYTE", "WORD", "RESB", "RESW"]

symbol_table = {}

def is_instruction(code):#cheak  code in instruction_set or code in pseudo_list (True or False )
    return code in instruction_set or code in pseudo_list


def parse_line(line: str):

    # Check if the line is a comment or an empty line
    if line.startswith((".", "\n")):
        return {"content": line}

    code = line.split() # Split the line into a list of words

    # Check if the line has three elements, and the second element is an instruction or pseudo-instruction
    if len(code) == 3 and (code[1] in instruction_set or code[1] in pseudo_list):
        return {"content": line, "symbol": code[0], "instruction": code[1], "args": code[2]}
    # Check if the line has two elements, and the first element is not an instruction or pseudo-instruction
    elif len(code) == 2 and not is_instruction(code[0]):
        return {"content": line, "symbol": code[0], "instruction": code[1], "args": ""}
    # Check if the line has two elements, and the first element is not an instruction or pseudo-instruction
    elif len(code) == 2 and is_instruction(code[0]):
        return {"content": line, "symbol": "", "instruction": code[0], "args": code[1]}
    # Check if the line has a single element, and the element is an instruction or pseudo-instruction
    elif is_instruction(code[0]):
        return {"content": line, "symbol": "", "instruction": code[0], "args": ""}
    # If none of the above conditions are met, raise an exception
    else:
        raise Exception("error")
    return line


def set_locctr(data, line):
    # first line
    if len(data) == 0:   #checks if the input list data is empty
        line["locctr"] = int(line["args"], 16)
        return data + [line]

    last_line = data[-1]
    last_locctr = last_line["locctr"]

    if "instruction" not in last_line:
        line["locctr"] = last_locctr + 0
    elif last_line["instruction"] == "START":
        line["locctr"] = last_locctr + 0
    elif last_line["instruction"] == "WORD":
        line["locctr"] = last_locctr + 3
    elif last_line["instruction"] == "BYTE" and last_line["args"][0] == "C":
        length = len(last_line["args"][2:-1].encode())
        line["locctr"] = last_locctr + length
    elif last_line["instruction"] == "RESW":
        line["locctr"] = last_locctr + int(last_line["args"]) * 3
    elif last_line["instruction"] == "RESB":
        line["locctr"] = last_locctr + int(last_line["args"])
    else:
        line["locctr"] = last_locctr + 3
    return data + [line]


def set_symbol_table(data, line):
    if "symbol" in line and line["symbol"]:
        data[line["symbol"]] = line["locctr"]
    return data


def set_object_code(data, line: dict):
    line["object_code"] = ""
    if "instruction" not in line:
        return data + [line]

    if line["instruction"] == "WORD":
        line["object_code"] = "{:0>6x}".format(int(line["args"]))
    elif line["instruction"] == "BYTE" and line["args"][0] == "C":
        args = line["args"][2:-1]
        line["object_code"] = hexlify(bytearray(args, "ascii")).decode()
    elif line["instruction"] in instruction_set:
        calc_code = instruction_set[line["instruction"]] << 16
        if line["args"]:
            calc_code += symbol_table[line["args"].split(",")[0]]
            if line["args"][-1] == "X":
                calc_code += 0x8000

        line["object_code"] = "{:0>6x}".format(calc_code)
        pass

    line["object_code"] = line["object_code"].upper()
    return data + [line]


def output_loc(data):
    with open("loc.txt", "w") as file:
        for line in data:
            if "instruction" in line:
                file.write("{:X}\t{}\t{}\t{}\n".format(
                    line["locctr"], line["symbol"], line["instruction"], line["args"]))
            else:
                file.write(line["content"])


def output_object_code(data):
    with open("Ans.txt", "w") as file:
        for line in data:
            if "instruction" in line:
                file.write("{:X}\t{}\t{}\t{}\t{}\n".format(
                    line["locctr"], line["symbol"], line["instruction"], line["args"], line["object_code"]))
            else:
                file.write(line["content"])


def output_object_Program(data: list):
    with open("ObjectProgram.txt", "w") as file:
        program_name = data[0].get("symbol", "")
        start_addr = data[0].get("locctr", 0x0100)
        start_line = [line for line in data if line.get(
            "instruction") == "START"]
        end_line = [line for line in data if line.get("instruction") == "END"]
        program_length = end_line[0]["locctr"] - start_line[0]["locctr"]
        file.write("H{:<6}{:0>6X}{:0>6X}\n".format(
            program_name, start_addr, program_length))

        record_line = ""
        object_code_line = ""
        for i, line in enumerate([i for i in data[1:] if "instruction" in i]):
            if not record_line and line["object_code"]:
                record_line = "T{:0>6X}".format(line["locctr"])
                object_code_line = line["object_code"]
            elif not line["object_code"] and object_code_line:
                file.write("{}{:0>2X}{}\n".format(record_line,int(len(object_code_line)/2), object_code_line))
                record_line = ""
                object_code_line = ""
            elif (len(object_code_line) + len(line["object_code"])) > 60:
                file.write("{}{:0>2X}{}\n".format(record_line,int(len(object_code_line)/2), object_code_line))
                record_line = "T{:0>6X}".format(line["locctr"])
                object_code_line = line["object_code"]
            else:
                object_code_line += line["object_code"]

        # eof
        file.write("E{:0>6X}".format(start_addr))


if __name__ == "__main__":
    data = []
    with open("CODE.txt", "r") as file:
        data = map(parse_line, file.readlines())

    data = reduce(set_locctr, data, [])
    symbol_table = reduce(set_symbol_table, data, {})
    data = reduce(set_object_code, data, [])
    output_loc(data)
    output_object_code(data)
    output_object_Program(data)