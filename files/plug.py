#!/usr/bin/python3
import os
import argparse
import json
import Extracting_data
import add_in_out
import shutil
import math
import re
from colorama import Fore
LAGO_DIR = ''
Top_level_file = ''
#################### LAGO ROOT address #######################################


def LAGO_USR_INFO():
    global LAGO_DIR, Top_level_file, file, top_file
    Linux_file_path = os.path.expanduser("~/.LAGO_USR_INFO")
    with open(Linux_file_path, "r") as Shell_file:
        sh_file = Shell_file.readlines()
        LAGO_DIR = sh_file[0].replace("LAGO_DIR=", "")+"/files/"
        if top_file:
            if f"TOP_FILE={top_file}\n" in sh_file:
                Top_level_file = top_file
            else:
                print(f"{top_file} is not present")
                exit()
        else:
            Top_level_file = sh_file[-1]
    LAGO_DIR = LAGO_DIR.replace("\n", "")
    Top_level_file = Top_level_file.replace("TOP_FILE=", '')


##############################################################################
CURRENT_DIR = os.getcwd()

def copy_file(file):
    global CURRENT_DIR, library_file
    if not os.path.exists(f"{CURRENT_DIR}/{file}"):
        shutil.copy(library_file, CURRENT_DIR)


def extract_data(file):                   # it will open library file
    global Top_level_file, CURRENT_DIR, instance
    with open(f"{file}", 'r') as f:
        lines = f.readlines()
    in_module = False
    input_or_output_count = 0
    output_string = ""
    for line in lines:
        if 'module' in line and not in_module:
            in_module = True
            module_name = line.split()[1]
            output_string += module_name + ' ' + f'{instance}' + '\n'
            output_string += "(\n"
        if 'input' in line or 'output' in line:
            input_or_output_count += 1
            words = line.strip().split()
            x = words[-1]
            if "," in x:
                x = x.split(",")[0]
            if input_or_output_count == sum(('input' in line) or ('output' in line) for line in lines):
                output_string += '.' + x + '\t\t\t()\n'
            else:
                output_string += '.' + x + '\t\t\t(),\n'

    # open top level file for inst checking
    with open(f"{CURRENT_DIR}/{Top_level_file}", "r") as f:
        content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if instance in line and ('input' or 'output') not in line:
                print(Fore.RED +
                      f'Error: instance {instance} already exists at line {i+1}. Please Enter different name!' + Fore.RESET)
                exit()
        with open(f"{CURRENT_DIR}/{Top_level_file}", "a+") as f:  # open top file in append mode
            if 'endmodule' in content:
                r_end = (f.tell())-9
                x = f.truncate(r_end)
                f.write('\n\n' + output_string)
                f.write(');')
                f.write('\n\nendmodule')
            print(
                Fore.GREEN + f'instance {instance} is successfully pluged in {Top_level_file}.' + Fore.RESET)

def io_outside(ios):
    global Top_level_file, CURRENT_DIR
    m_name = f"{Top_level_file}".replace(".sv", "")
    with open(f"{CURRENT_DIR}/{Top_level_file}", 'r') as f:
        file_contents = f.read()
    pattern = rf".*?(module\s+{m_name}\s*((?:[\s\S]*?);))"
    match = re.search(pattern, file_contents)
    if match:
        block = match.group(1)
        new_data = block + f"\n{ios}"
        file_contents = re.sub(pattern, new_data, file_contents)
        with open(f"{CURRENT_DIR}/{Top_level_file}", 'w') as f:
            f.write(file_contents)

def generating_mux(input_signals, output_signal, sl):
    leng = len(input_signals)
    rounding_threshold = 0.1
    val = math.log2(leng)
    if leng == 2:
        selct_lin = f'reg\t\t{sl};'
        io_outside(selct_lin)
        code = "always@*\n"
        code += f"\tcase({sl})\n"
        for i, signal in enumerate(input_signals):
            code += f"\t1'd{i}: {str(output_signal)} = {signal};\n"
        code += "\tendcase\n"
        mux_code = code
    else:
        if val - math.floor(val) > rounding_threshold:
            rounded_value = math.ceil(val)
        else:
            rounded_value = math.floor(val)

        selct_lin = f'reg [{rounded_value-1}:0] {sl};'
        io_outside(selct_lin)

        for i_sig in input_signals:
            ranges = f"[{rounded_value-1}:0]"
            signlas = f'reg {ranges} {i_sig};'
            io_outside(signlas)

            code = "always@*\n"
            code += f"\tcase({sl})\n"
            for i, signal in enumerate(input_signals):
                code += f"\t{rounded_value}'d{i}: {str(output_signal)} = {signal};\n"
            code += "\tendcase\n"
            mux_code = code

    # open top file in append mode
    with open(f"{CURRENT_DIR}/{Top_level_file}", "r") as f:
        content = f.read()
    with open(f"{CURRENT_DIR}/{Top_level_file}", "a+") as f:
        if 'endmodule' in content:
            r_end = (f.tell())-9
            x = f.truncate(r_end)
            f.write('\n' + mux_code)
            f.write('\nendmodule')
    return mux_code

def generate_register(inp_sig=None,inp_ranges=None, out_sig=None ,out_ranges=None, enable_sig=None):
    if enable_sig is None:
        if inp_sig:
            if inp_ranges is None:
                inp_declaration = f'reg {inp_sig};'
                io_outside(inp_declaration)
            else:
                inp_declaration = f'reg {inp_ranges} {inp_sig};'
                io_outside(inp_declaration)
        if out_sig:
            if out_ranges is None:
                out_declaration = f'reg {out_sig};'
                io_outside(out_declaration)
            else:
                out_declaration = f'reg {out_ranges} {out_sig};'
                io_outside(out_declaration)
                    
        code = f"always @(posedge clk)\nbegin\n\tif(reset)\n\tbegin\n"
        code += f"\t\t{out_sig} <= 0;\n"
        code += f"\tend\n\telse\n\tbegin\n"
        code += f"\t\t{out_sig} <= {inp_sig};\n"
        code += f"\tend\nend\n"
    else:
        reg_sig = f'reg {enable_sig};'
        io_outside(reg_sig)
        if inp_sig:
            if inp_ranges is None:
                inp_declaration = f'reg {inp_sig};'
                io_outside(inp_declaration)
            else:
                inp_declaration = f'reg {inp_ranges} {inp_sig};'
                io_outside(inp_declaration)
        if out_sig:
            if out_ranges is None:
                out_declaration = f'reg {out_sig};'
                io_outside(out_declaration)
            else:
                out_declaration = f'reg {out_ranges} {out_sig};'
                io_outside(out_declaration)
                
        code = f"always @(posedge clk)\nbegin\n"
        code += f"\tif(reset)\n\tbegin\n"
        code += f"\t\t{out_sig} <= 0;\n"
        code += f"\tend\n\telse if({enable_sig})\n\tbegin\n"
        code += f"\t\t{out_sig} <= {inp_sig};\n"
        code += f"\tend\nend\n"

    with open(f"{CURRENT_DIR}/{Top_level_file}", "r") as f:
        content = f.read()
    with open(f"{CURRENT_DIR}/{Top_level_file}", "a+") as f:
        if 'endmodule' in content:
            r_end = (f.tell())-9
            x = f.truncate(r_end)
            f.write('\n' + code)
            f.write('\nendmodule')

    return code


def fileio(inputs, input_ranges, outputs, output_ranges):
    global Top_level_file, CURRENT_DIR
    m_name = f"{Top_level_file}".replace('.sv', "")
    with open(f"{CURRENT_DIR}/{Top_level_file}", "r") as f:
        file_contents = f.read()
    # pattern = r".*?(clock\s*((?:[\s\S]*?);))"
    pattern = rf".*?(module\s+{m_name}\s*((?:[\s\S]*?);))"
    match = re.search(pattern, file_contents)
    if match:
        block = match.group(1)
        Body = ""
        if inputs:
            for inp_range, input in zip(input_ranges, inputs):
                if inp_range == 'None':
                    input_str = f"reg \t\t{input};\n"
                    Body += input_str
                else:
                    input_str = f"reg\t {inp_range}\t{input};\n"
                    Body += input_str
        if outputs:
            for out_range, output in zip(output_ranges, outputs):
                if out_range == 'None':
                    output_str = f"wire\t\t{output};\n"
                    Body += output_str
                else:
                    output_str = f"wire {out_range}\t{output};\n"
                    Body += output_str

        new = block + f"\n{Body}"
        file_contents = re.sub(pattern, new, file_contents)
        with open(f"{CURRENT_DIR}/{Top_level_file}", "w") as f:
            f.write(file_contents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--instance_name', help='Name of instance')
    parser.add_argument('-f', '--file_name',
                        help='Name of file from which instance is taken', type=str)
    parser.add_argument('-t', '--top_file',
                        help='other top level file', type=str)
    parser.add_argument('-i', '--inputs',help='Input port name')
    parser.add_argument('-ir', '--input_ranges',help='Input port range')
    parser.add_argument('-o', '--outputs',help='Output port name')
    parser.add_argument('-or', '--output_ranges',help='Output port range')
    parser.add_argument('-is', '--input_signal', default=[], type=str,
                        nargs='+', help='Output port range')
    parser.add_argument('-os', '--output_signal', type=str,
                        help='Output port range')
    parser.add_argument('-sl', '--select_line', type=str, help='Select line')
    parser.add_argument('-re', '--reset_signal', type=str, help='Select line')
    parser.add_argument('-en', '--enable_signal', type=str, help='Select line')
    parser.add_argument('-op', '--operation', choices=['dec', 'add','reg'])
    args = parser.parse_args()

    file = args.file_name
    top_file = args.top_file
    
###################################################################################################
    info = LAGO_USR_INFO()  # ---->
    Baseboard_path = os.path.join(LAGO_DIR, 'Baseboard')

######################################################################################################
    # if args.inputs or args.outputs:
    if args.operation == 'add':
        add_in_out.add_inputs_outputs(           # add extra inputs and outputs
            Top_level_file, args.inputs, args.outputs, args.input_ranges, args.output_ranges, Baseboard_path)
    if args.operation == 'dec':
        fileio(args.inputs, args.input_ranges,
               args.outputs, args.output_ranges)

    if args.input_signal:
        input_signals = args.input_signal
        output_signal = args.output_signal
        select_line = args.select_line
        data = generating_mux(input_signals, output_signal, select_line)
    if args.operation == 'reg':
        inp_signal = args.inputs
        out_signal = args.outputs
        enable_signal = args.enable_signal
        inp_ranges = args.input_ranges
        out_ranges = args.output_ranges
        generate_register(inp_signal,inp_ranges,out_signal,out_ranges,enable_signal)
#####################################################################################################
    if file and Top_level_file:
        library = os.path.join(LAGO_DIR, 'library')
        library_file = os.path.join(library, file)  # --->

        if args.instance_name:
            instance = args.instance_name
        else:
            instance = file.replace(".sv", '')

        copy_file(library_file)
        extract_data(library_file)
        data = Extracting_data.get_ranges_from_file(library_file)
        Top_level_file = Top_level_file.replace(".sv", '')
        with open(f"{Baseboard_path}/{Top_level_file}.json", "rb") as f:
            content = f.read()
            f.seek(0, 2)
        with open(f'{Baseboard_path}/{Top_level_file}.json', 'a+') as f:
            r_end = (f.tell())-1
            x = f.truncate(r_end)
            f.write(f',\n\"{instance}\":')
            json.dump(data, f, indent=4)
            f.write("\n}")
