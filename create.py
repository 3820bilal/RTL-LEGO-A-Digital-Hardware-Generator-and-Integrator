#!/usr/bin/env python3
import argparse
import os
import json
f_name = "Baseboard.sv"
folder_name = 'Baseboard'
input = ''
output = ''
child_path = r'..\LAGO\Baseboard'
######################### setting name of instance & body  ############################


def set_instance_name(f_name, inputs, outputs, input_ranges, output_ranges):
    m_name = f_name.replace(".sv", "")
    if inputs or outputs:
        Body = f"module {m_name} (\ninput\tlogic\t\tclk,\ninput\tlogic\t\treset,"
        if inputs:
            i = ""
            for inp, inp_ranges in zip(inputs, input_ranges):
                if inp_ranges == 'None':
                    inpo = f"\ninput\tlogic\t\t{(i.join(inp))},"
                    Body = Body + inpo
                elif inp_ranges is None:
                    inpo = f"\ninput\tlogic\t\t{(i.join(inp))},"
                    Body = Body + inpo
                else:
                    inpo = f"\ninput\tlogic\t\t{inp_ranges}\t\t{(i.join(inp))},"
                    Body = Body + inpo
        if outputs:
            o = ""
            for out, opt_ranges in zip(outputs, output_ranges):
                if opt_ranges == 'None':
                    outu = f"\noutput\tlogic\t\t{o.join(out)},"
                    Body = Body + outu
                elif opt_ranges is None:
                    outu = f"\noutput\tlogic\t\t{o.join(out)},"
                    Body = Body + outu
                else:
                    outu = f"\noutput\tlogic\t\t{opt_ranges}\t\t{o.join(out)},"
                    Body = Body + outu
        Body = Body.rstrip(",")
        end = "\n\n);\nendmodule"
        Body = Body + end
        print(Body)
    else:
        Body = f'''module {m_name} (\ninput\tlogic\t\tclk,\ninput\tlogic\t\treset,\n\n);\nendmodule'''
        print(Body)
    return Body


#########################################################


def default():
    global inputs, outputs, f_name, input_ranges, output_ranges
    print(f_name)
    print(os.getcwd())
    try:
        os.makedirs(folder_name)
        os.chdir(folder_name)
        with open(f_name, 'w+') as file:
            file.write(set_instance_name(f_name, inputs,
                       outputs, input_ranges, output_ranges))

            print(f"{f_name} created ")
    except:
        os.chdir(folder_name)
        with open(f_name, 'w+') as file:
            file.write(set_instance_name(f_name, inputs,
                       outputs, input_ranges, output_ranges))
            print(f"{f_name} created ")
#########################################################


def name():
    global inputs, outputs, input_ranges, output_ranges
    print(os.getcwd())
    try:
        os.chdir(folder_name)
        with open(f_name, 'w+') as file:
            file.write(set_instance_name(f_name, inputs,
                       outputs, input_ranges, output_ranges))
            print(f"{f_name} created ")
    except:
        os.makedirs(folder_name)
        os.chdir(folder_name)
        with open(f_name, 'w+') as file:
            file.write(set_instance_name(f_name, inputs,
                       outputs, input_ranges, output_ranges))
            print(f"{f_name} created ")


#########################################################
def storing_data_in_Json(f_name, inputs, input_ranges, outputs, output_ranges):
    m_name = f_name.replace(".sv", "")

    ports = {}
    ports["clk"] = {"type": "input", "range": "None"}
    ports["reset"] = {"type": "input", "range": "None"}

    if inputs:
        for i, inp in enumerate(inputs):
            if type(inp) == list:
                inp = inp[0]
            ports[inp] = {"type": "input", "range": input_ranges[i]}
    if outputs:
        for j, out in enumerate(outputs):
            if type(out) == list:
                out = out[0]
            ports[out] = {"type": "output", "range": output_ranges[j]}

    module_dict = {m_name: {"ports": ports}}
    return m_name, module_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename',
                        default="Baseboard.sv", help='Name of the file')
    parser.add_argument('-i', '--inputs', type=str,
                        nargs='+', help='Input port names')
    parser.add_argument('-ir', '--input_ranges', default='None', type=str,
                        nargs='+', help='Input port ranges')
    parser.add_argument('-o', '--outputs', type=str,
                        nargs='+', help='Output port names')
    parser.add_argument('-or', '--output_ranges', default='None',
                        nargs='+', help='Output port ranges')
    args = parser.parse_args()

    f_name = args.filename
    inputs = args.inputs
    input_ranges = args.input_ranges
    outputs = args.outputs
    output_ranges = args.output_ranges

    if f_name:
        name()
    else:
        default()
    m_name, module_dict = storing_data_in_Json(
        f_name, inputs, input_ranges, outputs, output_ranges)
    os.chdir('..')
    os.chdir('Baseboard')

    json_data = {
        "file_name": f"{f_name}",
        "folder_name": f"{folder_name}",
        "child_path": f"{child_path}"
    }
    with open("key_val_file.json", "w") as jsonfile:
        body = '{\n\"toplevelfile\":'
        end_body = '\n}'
        jsonfile.write(body)
        json.dump(json_data, jsonfile, indent=4)
        jsonfile.write(end_body)

    with open("key_val_file.json", "r") as f:
        content = f.read()
    with open('key_val_file.json', 'a+') as f:
        if "}" in content:
            r_end = (f.tell())-3
            x = f.truncate(r_end)
        f.write(',\n')
        f.write(f'\"{m_name}\":')
        json.dump(module_dict[m_name], f, indent=4)
        f.write("\n}")
